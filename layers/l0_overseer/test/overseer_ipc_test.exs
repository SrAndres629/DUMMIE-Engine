defmodule Overseer.IPCTest do
  use ExUnit.Case

  test "ping command returns pong" do
    # El PortManager ya está iniciado por la aplicación.
    assert {:ok, %{"pong" => true}} == Overseer.PortManager.send_command("ping")
  end
end

