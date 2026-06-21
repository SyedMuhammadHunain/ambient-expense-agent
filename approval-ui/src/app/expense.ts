import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface RunAgentRequest {
  appName: string;
  userId: string;
  sessionId: string;
  newMessage: {
    role: string;
    parts: any[];
  };
  streaming: boolean;
}

@Injectable({ providedIn: 'root' })
export class ExpenseService {
  private http = inject(HttpClient);

  resumeSession(userId: string, sessionId: string, message: string): Observable<any> {
    const payload: RunAgentRequest = {
      appName: 'expense_agent',
      userId,
      sessionId,
      newMessage: {
        role: 'user',
        parts: [
          {
            functionResponse: {
              id: 'human_approval',
              name: 'human_approval',
              response: { decision: message }
            }
          }
        ]
      },
      streaming: false
    };
    return this.http.post('/run', payload);
  }
}
