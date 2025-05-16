import { Injectable } from '@angular/core';
import {Observable, Subject} from "rxjs";

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {

  private socket!: WebSocket;
  private messageSubject = new Subject<any>();
  private httpUrl: string = "http://localhost:3000";

  constructor() {
    this.connect();
  }

  public connect(): void {
    this.socket = new WebSocket(this.httpUrl);

    this.socket.onopen = (event) => {
      console.log('WebSocket connected:', event);
    };

    this.socket.onmessage = (event) => {
      this.messageSubject.next(JSON.parse(event.data));
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.messageSubject.error(error);
    };

    this.socket.onclose = (event) => {
      console.log('WebSocket closed:', event);
      this.messageSubject.complete();
      // Optional: Reconnect logic
      setTimeout(() => this.connect(), 5000);
    };
  }

  public sendMessage(message: any): void {
    if (this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not open. Ready state:', this.socket.readyState);
    }
  }

  public getMessages(): Observable<any> {
    return this.messageSubject.asObservable();
  }

  public closeConnection(): void {
    this.socket.close();
  }
}
