package main

import "testing"

func TestShouldStartPortInterfaceDisabledByDefault(t *testing.T) {
	t.Setenv("DUMMIE_PORT_INTERFACE", "")

	if shouldStartPortInterface() {
		t.Fatal("port interface should be disabled by default for background daemon launches")
	}
}

func TestShouldStartPortInterfaceWhenExplicitlyEnabled(t *testing.T) {
	t.Setenv("DUMMIE_PORT_INTERFACE", "stdio")

	if !shouldStartPortInterface() {
		t.Fatal("port interface should be enabled when stdio mode is requested explicitly")
	}
}
