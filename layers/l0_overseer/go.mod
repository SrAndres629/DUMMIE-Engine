module io.dummie.v2/overseer

go 1.24.0

replace io.dummie.v2/nervous => ../l1_nervous

require (
	github.com/nats-io/nats.go v1.34.1
	io.dummie.v2/nervous v0.0.0
)

require (
	github.com/klauspost/compress v1.17.9 // indirect
	github.com/nats-io/nkeys v0.4.7 // indirect
	github.com/nats-io/nuid v1.0.1 // indirect
	golang.org/x/crypto v0.47.0 // indirect
	golang.org/x/sys v0.40.0 // indirect
	google.golang.org/protobuf v1.36.11 // indirect
)
