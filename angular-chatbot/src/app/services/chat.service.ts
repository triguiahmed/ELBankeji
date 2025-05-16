import { Injectable } from '@angular/core';
import {WebSocketService} from "./web-socket.service";
import {Observable} from "rxjs";

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  constructor(private websocketService: WebSocketService) {}

  sendMessage(message: string, sender: string): void {
    this.websocketService.sendMessage({
      type: 'message',
      content: message,
      sender: sender,
      timestamp: new Date().toISOString()
    });
  }

  getMessages(): Observable<any> {
    return this.websocketService.getMessages();
  }
}
