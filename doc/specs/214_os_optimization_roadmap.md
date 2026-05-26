# SPEC 214 — OS Optimization Roadmap Post-DUMMIE

**Status:** FUTURE (posterior a DUMMIE Engine 100% operativo)
**Categoría:** Visión de sistema operativo
**Dependencia:** DUMMIE Engine autónomo (L0-L2 completos)

---

## 1. Premisa

Una vez que DUMMIE Engine sea autosuficiente (capaz de escribir, probar y
desplegar código por sí mismo), se abren optimizaciones del sistema operativo
que hoy serían prematuras o riesgosas. DUMMIE podrá:

- Generar y probar módulos de kernel en aislamiento
- Simular cambios de scheduler, memoria y sysctl antes de aplicarlos
- Revertir automáticamente cualquier degradación

Este spec cataloga las optimizaciones identificadas pero postergadas.

---

## 2. Optimizaciones del Kernel y Memoria

### 2.1 zswap / zram — Compresión de RAM en caliente

- **Qué:** Comprimir páginas inactivas en RAM usando zstd/lz4
- **Ganancia estimada:** 2x-3x en densidad de memoria para cargas vectoriales
- **Riesgo:** Latencia en page fault (páginas comprimidas tardan en descomprimir)
- **Implementación:** `zswap.enabled=1 zswap.compressor=zstd`
  o zram para swap comprimido

### 2.2 KSM (Kernel Same-page Merging)

- **Qué:** Deduplicación de páginas idénticas entre procesos
- **Aplica a:** Múltiples agentes cargando los mismos embeddings, modelos,
  o librerías
- **Ganancia:** Alta cuando N agentes usan el mismo vector store
- **Riesgo:** CPU overhead en escaneo de páginas (configurable via
  `/sys/kernel/mm/ksm/`)

### 2.3 Transparent Hugepages + NUMA Tuning

- **Qué:** Asignar páginas de 2MB/1GB para reducir TLB misses en cargas
  de inferencia y embedding
- **Modo:** `madvise` en lugar de `always` (control granular por proceso)
- **NUMA binding:** Forzar procesos críticos (ollama, embedding service)
  al nodo NUMA de la GPU
- **Herramienta:** `numactl --cpunodebind=0 --membind=0`

### 2.4 CPU Isolation

- **Qué:** Aislar cores enteros para tareas de inferencia y scheduling
- **Mecanismo:** `isolcpus=nohz,domain` + `nohz_full=` en cmdline
- **Uso:** 2 cores para L0_overseer, 4 para L1_nervous, dejar dinámicos
  para L2_brain
- **Advertencia:** Requiere rebuild de initramfs y reboot

### 2.5 sysctl Performance Tuning

```
vm.swappiness=10           # Evitar swap innecesario
vm.vfs_cache_pressure=50   # Cachear dentries/inodes más tiempo
vm.dirty_ratio=30          # Dirty pages más agresivo para escritura
vm.dirty_background_ratio=5
kernel.numa_balancing=0    # Desactivar balanceo NUMA automático
net.core.rmem_max=134217728  # Aumentar buffers de red para IPC
net.core.wmem_max=134217728
```

---

## 3. Memoria Vectorial Nativa (Concepto)

### 3.1 Problema

La memoria actual se organiza por direcciones lineales. Dos páginas
adyacentes en el espacio de direcciones no tienen relación semántica.
Para encontrar datos por similitud, hay que embedderizar, indexar en una
estructura externa (HNSW, FAISS) y paginar sobre ella — todo en userspace.

### 3.2 Visión

Una abstracción de memoria donde el direccionamiento incluye **significado**.
El kernel entiende que los datos pueden organizarse por cercanía vectorial:

- `MAP_VECTOR`: nuevo flag de `mmap()` que asigna páginas indexadas por
  embedding. El proceso escribe y el kernel embeddingiza automáticamente.
- Page fault handler semántico: cuando se accede a una dirección vectorial,
  el kernel trae la página con datos semánticamente más cercanos.
- TLB extendida: caché de "dirección → región de similitud" en vez de
  "dirección → marco de página".

### 3.3 Arquitectura Propuesta (Opción Realista)

No un kernel monolítico, sino una **capa mixta**:

```
┌─────────────────────────────────────────┐
│  Userspace                               │
│  ┌────────────────┐  ┌────────────────┐  │
│  │ libvmem.so      │  │ DUMMIE Engine  │  │
│  │ mmap anon       │  │ (L1 nervous)   │  │
│  │ + ioctl vector  │  │ embeddingiza   │  │
│  └────┬───────────┘  └───────┬────────┘  │
│       │                      │            │
└───────┼──────────────────────┼────────────┘
        │ ioctl                │ hints
┌───────┼──────────────────────┼────────────┐
│ Kernel│                      │            │
│  ┌────┴──────────────────────┴──────┐     │
│  │  vmem.ko (módulo)                │     │
│  │  - nuevo VMA type: MAP_VECTOR    │     │
│  │  - page fault: consulta page     │     │
│  │    cluster por embedding         │     │
│  │  - sysfs: stats, hits, misses    │     │
│  └──────────────────────────────────┘     │
│  ┌────────────────────┐                   │
│  │  vstore.ko         │                   │
│  │  - kernel-space    │                   │
│  │    HNSW/FAISS      │                   │
│  │  - memory pool     │                   │
│  │    (contiguo)       │                   │
│  └────────────────────┘                   │
└───────────────────────────────────────────┘
```

#### Componentes

1. **vmem.ko** — Módulo de kernel que registra un nuevo tipo de VMA
   (`MAP_VECTOR`). Atrapa page faults y consulta vstore.ko para
   determinar qué página cargar. Expone estadísticas via sysfs.

2. **vstore.ko** — Indexador vectorial en kernel-space. Mantiene un
   grafo HNSW en un pool de memoria contiguo. Soporta insert, search,
   delete. El pool vive en memoria reservada al boot (memblock).

3. **libvmem.so** — Biblioteca userspace que envuelve `mmap(..., MAP_VECTOR)`
   y expone API tipo `vmem_store(ptr, len, embedding)` y
   `vmem_query(embedding, k) → vecinos`.

4. **DUMMIE Engine integration** — L1_nervous embeddingiza todos los
   datos de entrenamiento y los escribe en el espacio vectorial. L2_brain
   consulta el espacio para recuperación de contexto.

### 3.4 Viabilidad

| Aspecto | Estado |
|---------|--------|
| Kernel module API estable | Linux 6.12+ (nuestra versión) soporta `struct vm_operations_struct` completo |
| HNSW en kernel | No existe. Habría que portar una implementación minimalista, sin allocaciones dinámicas |
| Page fault semántico | El módulo puede decidir qué page-inject hacer en fault handler — viable |
| Consistencia | El kernel no debe hacer embedding en fault handler (demasiado lento). La embeddingización ocurre en userspace; el kernel solo indexa |
| Seguridad | MAP_VECTOR no debe exponer datos entre procesos — cada VMA es privada |

### 3.5 Riesgos

- **Latencia:** Un page fault vectorial sería órdenes de magnitud más
  lento que uno normal (microsegundos vs nanosegundos). Solo apto para
  regiones de memoria explícitamente marcadas.
- **Complejidad:** Módulo de kernel que maneja un grafo HNSW es frágil.
  Cualquier error = kernel panic.
- **Utilidad real:** Para la mayoría de los casos, un store HNSW en
  userspace con mmap a tmpfs da ~95% del beneficio con 5% del riesgo.

---

## 4. Implementación como Especificaciones

Cada optimización de las secciones 2 y 3 debería descomponerse en specs
individuales cuando llegue el momento:

| # | Título | Prioridad | Dependencia |
|---|--------|-----------|-------------|
| 214.1 | zswap/zram activation | media | DUMMIE test suite |
| 214.2 | KSM tuning | media | DUMMIE test suite |
| 214.3 | Hugepages + NUMA pinning | alta | Reboot |
| 214.4 | CPU isolation (isolcpus) | alta | Rebuild initramfs |
| 214.5 | sysctl baseline profile | baja | Ninguna |
| 214.6 | vmem.ko (kernel vector memory) | experimental | DUMMIE 100% |
| 214.7 | libvmem.so (userspace API) | experimental | vmem.ko |

---

## 5. Criterios para Comenzar

No empezar ninguna optimización de este spec hasta que:

1. DUMMIE Engine pase todas las pruebas de L0, L1, L2
2. DUMMIE pueda generar un módulo de kernel, compilarlo, cargarlo,
   probarlo y descargarlo autónomamente
3. Exista un entorno de pruebas aislado (QEMU + kernel custom) donde
   DUMMIE pueda iterar cambios de kernel sin riesgo al host
4. Las métricas de baseline estén capturadas (benchmarks de inferencia,
   embeddings, latencia de IPC, throughput de scheduling)

Solo entonces tiene sentido abordar la memoria vectorial nativa.
