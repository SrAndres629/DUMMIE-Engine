const std = @import("std");

/// 6D-Context: The Deterministic Vector (Spec 12)
pub const SixDimensionalContext = struct {
    locus_x: []const u8,
    locus_y: []const u8,
    locus_z: []const u8,
    lamport_t: u64,
    authority_a: u8,
    intent_i: u8,
};

/// 4D-TES: Immutable Memory Node (Spec 02)
pub const MemoryNode4DTES = struct {
    causal_hash: [64]u8,
    parent_hash: [64]u8,
    context: SixDimensionalContext,
    payload_hash: [64]u8,
};

/// Helper to format a hash to hex string
pub fn hashToHex(hash: [32]u8, out: *[64]u8) void {
    const hex_chars = "0123456789abcdef";
    for (hash, 0..) |b, i| {
        out[i * 2] = hex_chars[b >> 4];
        out[i * 2 + 1] = hex_chars[b & 0x0f];
    }
}
