import os
import time
import json
import signal
import psutil
import unittest
import subprocess

from web3 import Web3
from web3.middleware import geth_poa_middleware

from optimism import CrossChainMessenger

from test.utils import TestUtil

class TestDeposit(unittest.TestCase, TestUtil):

    def setUp(self) -> None:

        self.node_process = subprocess.Popen(["start_devnet", "devnode"])

        if self.node_process.returncode == None:
            print("Local dev net started successfully")
        else:
            print(f"Error starting local dev net. Exit code: {self.node_process.returncode}")

        time.sleep(40)

        subprocess.Popen(["sshpass", "-p", "sandbox", "ssh", "-o", "IdentitiesOnly=yes", "-t", "sandbox@127.0.0.1", "-p", "10022", "cd ~/optimism && make devnet-up"])

        time.sleep(40)

        vm_process = subprocess.Popen(["sshpass", "-p", "sandbox", "ssh", "-o", "IdentitiesOnly=yes", "-t", "sandbox@127.0.0.1", "-p", "10022", "python3 extract_addresses.py"], stdout=subprocess.PIPE)

        output, error = vm_process.communicate()
        if error:
            print(f"Error: {error}")
        else:
            l1_addresses_devnet = json.loads(output.decode().strip("\r\n").replace("'", "\""))

            with open("optimism/config.json", 'r') as file:
                addresses = json.load(file)

            addresses["900"]["901"]["l1_addresses"] = l1_addresses_devnet

            with open("optimism/config.json", 'w') as json_file:
                json.dump(addresses, json_file, indent=4)

        subprocess.Popen(["sshpass", "-p", "sandbox", "ssh", "-o", "IdentitiesOnly=yes", "-t", "sandbox@127.0.0.1", "-p", "10022", f"echo 'export L2OO_ADDRESS={l1_addresses_devnet['L2_OUTPUT_ORACLE']}' >> '/home/sandbox/.bashrc'"])
        subprocess.Popen(["sshpass", "-p", "sandbox", "ssh", "-o", "IdentitiesOnly=yes", "-t", "sandbox@127.0.0.1", "-p", "10022", f"cd ~/optimism && python3 bedrock-devnet/main.py"])

        time.sleep(20)

        self.l1_provider = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
        self.l2_provider = Web3(Web3.HTTPProvider("http://127.0.0.1:9545"))

        self.l1_provider.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.l2_provider.middleware_onion.inject(geth_poa_middleware, layer=0)

        self.faucet = self.l1_provider.eth.account.from_key("0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")

        self.account = self.l1_provider.eth.account.from_key("0x" + "1" * 64)

        self.fund_account(self.account, 10**18, layer="l1")


    
    def tearDown(self) -> None:
        print("Tearing down devnet")

        subprocess.Popen(["sshpass", "-p", "sandbox", "ssh", "-o", "IdentitiesOnly=yes", "-t", "sandbox@127.0.0.1", "-p", "10022", "cd ~/optimism && make devnet-down"])
        time.sleep(30)
        subprocess.Popen(["sshpass", "-p", "sandbox", "ssh", "-o", "IdentitiesOnly=yes", "-t", "sandbox@127.0.0.1", "-p", "10022", "cd ~/optimism && make devnet-clean"])
        time.sleep(30)
        subprocess.Popen(["sshpass", "-p", "sandbox", "ssh", "-o", "IdentitiesOnly=yes", "-t", "sandbox@127.0.0.1", "-p", "10022", "sudo poweroff"])
        time.sleep(10)

        node_process_pid = self.node_process.pid

        parent_process = psutil.Process(node_process_pid)
        child_processes = parent_process.children(recursive=True)

        self.node_process.terminate()

        # kill all child processes
        for child in child_processes:
            if parent_process.pid != child.pid:
                os.kill(child.pid, signal.SIGTERM)

    
    def testDepositETH(self):

        l1_chain_id = 900
        l2_chain_id = 901

        cross_chain_messenger = CrossChainMessenger(l1_chain_id, l2_chain_id, account_l1=self.account, account_l2=self.account, provider_l1=self.l1_provider, provider_l2=self.l2_provider)

        balance_l1 = self.l1_provider.eth.get_balance(self.account.address)
        balance_l2 = self.l2_provider.eth.get_balance(self.account.address)

        self.assertEqual(balance_l1, 10**18)
        self.assertEqual(balance_l2, 0)

        deposit_txn_hash, deposit_txn_receipt = cross_chain_messenger.deposit_eth(5*10**17)

        time.sleep(30)

        balance_l1 = self.l1_provider.eth.get_balance(self.account.address)
        balance_l2 = self.l2_provider.eth.get_balance(self.account.address)

        self.assertGreater(balance_l1, 0.498*10**18)
        self.assertLess(balance_l1, 0.5*10**18)

        self.assertEqual(balance_l2, 0.5*10**18)


        


        
