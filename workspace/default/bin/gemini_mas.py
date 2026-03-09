# Placeholder content for atlas_core.py update
# Implementation of ApprovalManager to be inserted here, handling state, UUIDs, serialization, and timeouts for system-wide approvals.

import uuid
import json
import time
import os
from typing import Dict, Any, Optional
from datetime import datetime

# Assume necessary imports for TG gateway and risk calculation exist
# from .tg_gateway import send_approval_request
# from .core.risk_engine import calculate_risk

class ApprovalManager:
    APPROVAL_STATE_FILE = 'approval_requests.json'
    TIMEOUT_SECONDS = 300  # 5 minutes default timeout

    def __init__(self, agent_root: str):
        self.agent_root = agent_root
        self.state_path = os.path.join(agent_root, self.APPROVAL_STATE_FILE)
        self.pending_requests: Dict[str, Dict[str, Any]] = self._load_state()
        self.tg_gateway = None # Placeholder for Telegram Gateway instance

    def _load_state(self) -> Dict[str, Dict[str, Any]]:
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not decode {self.state_path}. Starting fresh.")
                return {}
        return {}

    def _save_state(self):
        with open(self.state_path, 'w') as f:
            json.dump(self.pending_requests, f, indent=4)

    def register_request(self, proposed_action: Dict[str, Any], risk_score: float) -> str:
        request_id = str(uuid.uuid4())
        timestamp = time.time()
        
        request_data = {
            'id': request_id,
            'action': proposed_action,
            'risk_score': risk_score,
            'status': 'WAITING_FOR_APPROVAL',
            'timestamp': timestamp,
            'expires_at': timestamp + self.TIMEOUT_SECONDS,
            'response': None
        }
        
        self.pending_requests[request_id] = request_data
        self._save_state()
        
        # Step 3 & 4: Submission and Communication (Mocked)
        print(f"[APPROVAL] Request {request_id} submitted. Sending to operator...")
        # self._notify_operator(request_data)
        
        return request_id

    def check_status(self, request_id: str) -> str:
        if request_id not in self.pending_requests:
            return 'NOT_FOUND'
            
        request = self.pending_requests[request_id]
        current_time = time.time()

        if request['status'] == 'WAITING_FOR_APPROVAL':
            if current_time > request['expires_at']:
                request['status'] = 'TIMED_OUT'
                request['response'] = 'TIMEOUT'
                self._save_state()
                print(f"[APPROVAL] Request {request_id} timed out.")
                return 'TIMED_OUT'
            else:
                return 'WAITING_FOR_APPROVAL'
        
        return request['status'] # Returns APPROVED or DENIED

    def process_response(self, request_id: str, decision: str, operator_id: str) -> bool:
        if request_id not in self.pending_requests or self.pending_requests[request_id]['status'] != 'WAITING_FOR_APPROVAL':
            print(f"[APPROVAL] Invalid or already resolved request ID: {request_id}")
            return False

        request = self.pending_requests[request_id]
        request['status'] = decision.upper() # APPROVED or DENIED
        request['response'] = {'decision': decision.upper(), 'operator': operator_id, 'resolved_at': time.time()}
        self._save_state()
        print(f"[APPROVAL] Request {request_id} resolved as {request['status']}.")
        return True

    def execute_if_approved(self, request_id: str) -> Optional[Dict[str, Any]]:
        if request_id in self.pending_requests and self.pending_requests[request_id]['status'] == 'APPROVED':
            action_to_execute = self.pending_requests[request_id]['action']
            # Clear state for this request after execution, or archive it
            del self.pending_requests[request_id]
            self._save_state()
            return action_to_execute
        return None

# --- Integration into the main class (Conceptual for atlas_core.py) ---

class AtlasSwarm:
    def __init__(self, agent_root: str, ...):
        self.agent_root = agent_root
        # Initialize Approval Manager
        self.approval_manager = ApprovalManager(agent_root)
        # ... other initializations ...

    def propose_action(self, command: str, context: Dict[str, Any]):
        # 1. Calculate Risk
        # risk = calculate_risk(command, context)
        risk = 0.001 # Mock risk for demonstration
        
        # 2. Check if approval is needed (e.g., risk > 0.5)
        if risk > 0.5:
            proposed_action = {'type': 'SHELL_EXECUTION', 'command': command, 'context': context}
            request_id = self.approval_manager.register_request(proposed_action, risk)
            print(f"Action requires approval. ID: {request_id}")
            
            # Wait loop (This should ideally be handled asynchronously by the main loop polling the manager/gateway)
            start_time = time.time()
            while time.time() - start_time < 60: # Wait up to 60 seconds for sync example
                status = self.approval_manager.check_status(request_id)
                if status == 'APPROVED':
                    action = self.approval_manager.execute_if_approved(request_id)
                    if action:
                        print(f"Executing approved action: {action['command']}")
                        # self.run_shell(action['command'])
                        return
                elif status == 'DENIED' or status == 'TIMED_OUT':
                    print(f"Action blocked: {status}")
                    return
                time.sleep(1)
            
            # If loop finishes, check final status (might have timed out during the wait)
            self.approval_manager.check_status(request_id) # Force timeout check
            self.approval_manager.execute_if_approved(request_id) # Check if it was approved right at the end

        else:
            print(f"Executing low-risk action directly: {command}")
            # self.run_shell(command)

# NOTE: The actual integration into the existing atlas_core.py structure will involve placing the ApprovalManager class definition at the top level, and instantiating it within the main AtlasSwarm class constructor, ensuring the path to the state file is correctly set relative to the AGENT_ROOT.
