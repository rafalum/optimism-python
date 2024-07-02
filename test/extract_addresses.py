import json

# Load the JSON data from the new file
with open('/home/sandbox/optimism/packages/contracts-bedrock/deployments/31337-deploy.json') as f:
    data = json.load(f)

# Extract the addresses based on the keys provided in the new JSON file
addresses = {
    "OPTIMISM_PORTAL": data.get("OptimismPortal2"),
    "L1_STANDARD_BRIDGE": data.get("L1StandardBridgeProxy"),
    "L1_CROSS_CHAIN_MESSENGER": data.get("L1CrossDomainMessengerProxy"),
    "L2_OUTPUT_ORACLE": data.get("L2OutputOracleProxy"),
    "DISPUTE_GAME_FACTORY": data.get("DisputeGameFactoryProxy")
}

# Print the addresses
print(addresses)
