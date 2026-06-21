import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  template: '<main class="min-h-screen bg-gray-100"><router-outlet></router-outlet></main>',
  styleUrl: './app.css'
})
export class App {}
