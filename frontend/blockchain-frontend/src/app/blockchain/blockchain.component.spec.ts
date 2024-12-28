import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-blockchain',
  standalone: true,
  templateUrl: './blockchain.component.html', // Reference the external HTML file
  imports: [FormsModule], // Include FormsModule for ngModel support
})
export class BlockchainComponent {

}
