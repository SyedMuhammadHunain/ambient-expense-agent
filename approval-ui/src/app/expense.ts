import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ResumePayload {
  user_id: string;
  session_id: string;
  message: string;
}

@Injectable({ providedIn: 'root' })
export class ExpenseService {
  private http = inject(HttpClient);

  resumeSession(payload: ResumePayload): Observable<any> {
    return this.http.post('/apps/expense_agent/run', payload);
  }
}
