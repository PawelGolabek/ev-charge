import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { BlockchainComponent } from './blockchain/blockchain.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, BlockchainComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'blockchain-frontend';
}
