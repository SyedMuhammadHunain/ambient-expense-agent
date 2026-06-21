import { Component, inject, signal } from '@angular/core';
import { ExpenseService } from '../expense';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class Dashboard {
  private expenseService = inject(ExpenseService);

  sessionId = signal('test-sub');
  userId = signal('default');
  status = signal('');
  isLoading = signal(false);

  updateSessionId(event: Event) {
    this.sessionId.set((event.target as HTMLInputElement).value);
  }

  updateUserId(event: Event) {
    this.userId.set((event.target as HTMLInputElement).value);
  }

  approve() {
    this.isLoading.set(true);
    this.status.set('Submitting approval...');
    this.expenseService.resumeSession(
      this.userId(),
      this.sessionId(),
      'approve'
    ).subscribe({
      next: (res) => {
        this.status.set('✅ Approved: ' + JSON.stringify(res));
        this.isLoading.set(false);
      },
      error: (err) => {
        this.status.set('❌ Error: ' + (err.error?.detail || err.message));
        this.isLoading.set(false);
      }
    });
  }

  reject() {
    this.isLoading.set(true);
    this.status.set('Submitting rejection...');
    this.expenseService.resumeSession(
      this.userId(),
      this.sessionId(),
      'reject'
    ).subscribe({
      next: (res) => {
        this.status.set('🚫 Rejected: ' + JSON.stringify(res));
        this.isLoading.set(false);
      },
      error: (err) => {
        this.status.set('❌ Error: ' + (err.error?.detail || err.message));
        this.isLoading.set(false);
      }
    });
  }
}
