import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-blockchain',
  standalone: true,
  templateUrl: './blockchain.component.html', // Reference the external HTML file
  imports: [FormsModule], // Include FormsModule for ngModel support
})
export class BlockchainComponent {
  txId: string = '';
  amount: number = 0;
  verifyTxId: string = '';
  result: string = '';
  baseUrl: string = 'http://127.0.0.1:5000'; // Base URL for API calls

  async submitTransaction() {
    if (!this.txId || this.amount <= 0) {
      alert('Please enter both Transaction ID and a valid Amount');
      return;
    }

    try {
      const response = await fetch(`${this.baseUrl}/submit_transaction`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tx_id: this.txId, amount: this.amount })
      });
      const data = await response.json();
      this.result = JSON.stringify(data, null, 2);
    } catch (error) {
      console.error('Error:', error);
      this.result = 'An error occurred. Check console for details.';
    }
  }

  async verifyTransaction() {
    if (!this.verifyTxId) {
      alert('Please enter a Transaction ID');
      return;
    }

    try {
      const response = await fetch(`${this.baseUrl}/verify_transaction`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tx_id: this.verifyTxId })
      });
      const data = await response.json();
      this.result = JSON.stringify(data, null, 2);
    } catch (error) {
      console.error('Error:', error);
      this.result = 'An error occurred. Check console for details.';
    }
  }

  async getAllTransactions() {
    try {
      const response = await fetch(`${this.baseUrl}/get_all_transactions`);
      const data = await response.json();
      this.result = JSON.stringify(data, null, 2);
    } catch (error) {
      console.error('Error:', error);
      this.result = 'An error occurred. Check console for details.';
    }
  }
}
