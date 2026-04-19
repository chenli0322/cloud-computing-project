// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title HealthLog
 * @notice Append-only registry of detected health anomalies.
 *
 * Design rationale (hybrid Web2 + Web3, per Prof. Franchitti 4/16 guidance):
 *   - Raw sensor data and ML outputs stay off-chain (P2P + S3).
 *   - Only the SHA-256 hash + timestamp of each anomaly event is written
 *     on-chain, giving an immutable, publicly-verifiable audit trail
 *     without blowing up gas costs.
 *
 * Anyone can verify an off-chain anomaly record by re-hashing it and
 * calling `exists(hash)`.
 */
contract HealthLog {
    struct Entry {
        bytes32 eventHash;      // sha256 of the off-chain JSON event
        uint256 timestamp;      // block time when logged
        address reporter;       // node that submitted the record
        string  deviceId;       // e.g. "sim-device-001"
        string  anomalyKind;    // e.g. "hr_high"
    }

    Entry[] public entries;
    mapping(bytes32 => uint256) public indexOfHash;   // hash -> entries index+1

    event AnomalyLogged(
        bytes32 indexed eventHash,
        address indexed reporter,
        string  deviceId,
        string  anomalyKind,
        uint256 timestamp
    );

    function logAnomaly(
        bytes32 eventHash,
        string calldata deviceId,
        string calldata anomalyKind
    ) external returns (uint256 id) {
        require(indexOfHash[eventHash] == 0, "duplicate event");
        entries.push(Entry({
            eventHash:   eventHash,
            timestamp:   block.timestamp,
            reporter:    msg.sender,
            deviceId:    deviceId,
            anomalyKind: anomalyKind
        }));
        id = entries.length;            // 1-indexed
        indexOfHash[eventHash] = id;
        emit AnomalyLogged(eventHash, msg.sender, deviceId, anomalyKind, block.timestamp);
    }

    function exists(bytes32 eventHash) external view returns (bool) {
        return indexOfHash[eventHash] != 0;
    }

    function total() external view returns (uint256) {
        return entries.length;
    }

    function getEntry(uint256 id) external view returns (Entry memory) {
        require(id >= 1 && id <= entries.length, "bad id");
        return entries[id - 1];
    }
}
