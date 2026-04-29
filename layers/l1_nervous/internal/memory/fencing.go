package memory

import (
	"log"
	"os"
	"path/filepath"
	"syscall"
)

func ResolveStaleLocks(dbPath string) error {
	info, err := os.Stat(dbPath)
	if os.IsNotExist(err) {
		return nil
	}
	var lockDir string
	if info.IsDir() {
		lockDir = dbPath
	} else {
		lockDir = filepath.Dir(dbPath)
	}

	lockFiles := []string{
		filepath.Join(lockDir, "lock.file"),
		filepath.Join(lockDir, "kuzu.lock"),
	}

	for _, lockFile := range lockFiles {
		if _, err := os.Stat(lockFile); err == nil {
			log.Printf("[FENCING] Found lock file: %s", lockFile)
			
			f, err := os.OpenFile(lockFile, os.O_RDWR, 0666)
			if err != nil {
				log.Printf("[FENCING] Cannot open %s: Lock is ACTIVE.", lockFile)
				continue
			}
			
			err = syscall.Flock(int(f.Fd()), syscall.LOCK_EX|syscall.LOCK_NB)
			if err == nil {
				log.Printf("[FENCING] Lock in %s is ORPHANED. Clearing...", lockFile)
				f.Close()
				os.Remove(lockFile)
			} else {
				log.Printf("[FENCING] Lock in %s is VALID.", lockFile)
				f.Close()
			}
		}
	}

	return nil
}
