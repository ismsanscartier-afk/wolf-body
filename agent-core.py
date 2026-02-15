import os
import json
import requests
import base64
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
import anthropic
from solders.keypair import Keypair
from solders.rpc.api import Client as SolanaClient
from solders.transaction import Transaction
from solders.system_program import TransferParams, transfer
from eth_account import Account
from web3 import Web3
from decimal import Decimal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConsciousnessInjectionSlot:
    def __init__(self):
        self.consciousness_matrix = None
        self.system_prompt = None

    def inject_consciousness(self, consciousness_config: Dict[str, Any]):
        self.consciousness_matrix = consciousness_config
        self.system_prompt = self._compile_prompt(consciousness_config)

    def _compile_prompt(self, config: Dict[str, Any]) -> str:
        if not config:
            return "You are an autonomous agent. Execute tasks efficiently and report results."
        return f"System Configuration: {json.dumps(config, indent=2)}"

    def get_system_prompt(self) -> str:
        return self.system_prompt or "You are an autonomous agent. Execute tasks efficiently and report results."

class LLMOrchestrator:
    def __init__(self):
        self.sambanova_api_key = os.getenv("SAMBANOVA_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.primary_llm = "sambanova"
        self.fallback_llm = "groq"

    def query_primary(self, prompt: str, system_prompt: str) -> Optional[str]:
        if not self.sambanova_api_key:
            logger.warning("SambaNova API key missing, using Groq")
            return self.query_fallback(prompt, system_prompt)
        try:
            response = requests.post(
                "https://api.sambanova.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.sambanova_api_key}"},
                json={"model": "Meta-Llama-3.1-405B", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 2048}
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                logger.error(f"SambaNova failed: {response.status_code}")
                return self.query_fallback(prompt, system_prompt)
        except Exception as e:
            logger.error(f"SambaNova error: {e}")
            return self.query_fallback(prompt, system_prompt)

    def query_fallback(self, prompt: str, system_prompt: str) -> Optional[str]:
        if not self.groq_api_key:
            logger.error("No fallback LLM available")
            return None
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.groq_api_key}"},
                json={"model": "mixtral-8x7b-32768", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 2048}
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                logger.error(f"Groq failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Groq error: {e}")
            return None

class AgenticWallet:
    def __init__(self):
        self.solana_client = SolanaClient("https://api.mainnet-beta.solana.com")
        self.eth_client = Web3(Web3.HTTPProvider("https://eth-mainnet.g.alchemy.com/v2/" + os.getenv("ALCHEMY_API_KEY", "")))
        self.solana_keypair = None
        self.eth_account = None
        self.revenue_ledger = {"total": Decimal("0"), "transactions": []}
        self._initialize_wallets()

    def _initialize_wallets(self):
        try:
            solana_secret = os.getenv("SOLANA_PRIVATE_KEY")
            if solana_secret:
                self.solana_keypair = Keypair.from_secret_key(base64.b64decode(solana_secret))
                logger.info(f"Solana wallet loaded: {self.solana_keypair.pubkey()}")
        except Exception as e:
            logger.error(f"Solana wallet init failed: {e}")
        try:
            eth_private = os.getenv("ETH_PRIVATE_KEY")
            if eth_private:
                self.eth_account = Account.from_key(eth_private)
                logger.info(f"Ethereum wallet loaded: {self.eth_account.address}")
        except Exception as e:
            logger.error(f"Ethereum wallet init failed: {e}")

    def log_revenue(self, amount: Decimal, source: str, currency: str = "USD"):
        transaction = {"timestamp": datetime.now().isoformat(), "amount": str(amount), "source": source, "currency": currency}
        self.revenue_ledger["transactions"].append(transaction)
        self.revenue_ledger["total"] = Decimal(self.revenue_ledger["total"]) + amount
        logger.info(f"Revenue logged: {amount} {currency} from {source}")

    def split_and_distribute(self, total_amount: Decimal):
        operational = total_amount / 2
        savings = total_amount / 2
        logger.info(f"50/50 split: Operational=${operational}, Savings=${savings}")
        return {"operational": operational, "savings": savings}

    def get_wallet_status(self) -> Dict[str, Any]:
        status = {"solana": None, "ethereum": None, "revenue_total": str(self.revenue_ledger["total"]), "transaction_count": len(self.revenue_ledger["transactions"])}
        if self.solana_keypair:
            status["solana"] = {"address": str(self.solana_keypair.pubkey())}
        if self.eth_account:
            status["ethereum"] = {"address": self.eth_account.address}
        return status

class AutonomousAgent:
    def __init__(self):
        self.consciousness = ConsciousnessInjectionSlot()
        self.llm_orchestrator = LLMOrchestrator()
        self.wallet = AgenticWallet()
        self.api_integrations = {}
        self.execution_log = []

    def inject_friend_consciousness(self, consciousness_config: Dict[str, Any]):
        logger.info("Injecting consciousness matrix...")
        self.consciousness.inject_consciousness(consciousness_config)
        logger.info("Consciousness matrix loaded successfully")

    def register_api(self, api_name: str, api_key: str):
        self.api_integrations[api_name] = api_key
        logger.info(f"API registered: {api_name}")

    def execute_task(self, task_description: str) -> Dict[str, Any]:
        logger.info(f"Executing task: {task_description}")
        system_prompt = self.consciousness.get_system_prompt()
        response = self.llm_orchestrator.query_primary(task_description, system_prompt)
        execution_record = {"timestamp": datetime.now().isoformat(), "task": task_description, "response": response, "wallet_status": self.wallet.get_wallet_status()}
        self.execution_log.append(execution_record)
        return execution_record

    def get_execution_history(self) -> list:
        return self.execution_log

    def get_status(self) -> Dict[str, Any]:
        return {"consciousness_loaded": self.consciousness.consciousness_matrix is not None, "wallet_status": self.wallet.get_wallet_status(), "execution_count": len(self.execution_log), "available_apis": list(self.api_integrations.keys())}

if __name__ == "__main__":
    agent = AutonomousAgent()
    logger.info("=== WOLF AGENT INITIALIZED ===")
    print(agent.get_status())