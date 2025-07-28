import { Injectable } from '@angular/core';
import { MessageInfo } from '../utils/message-info';

@Injectable({
  providedIn: 'root'
})
export class ToasterService {
  constructor(private msgInfo: MessageInfo) {}

  private createToast(message: string, type: 'success' | 'error') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerText = message;

    document.body.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('show');
    }, 100);

    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => {
        document.body.removeChild(toast);
      }, 300);
    }, 5000);
  }

  success(msgCode: number) {
    const message = this.msgInfo.getMessage(msgCode);
    this.createToast(`${message}`, 'success');
  }

  failure(msgCode: number) {
    const message = this.msgInfo.getMessage(msgCode);
    this.createToast(`${message}`, 'error');
  }

  failureWithMessage(msg: string, msgCode?: number) {
    let message = msg;
    if (msgCode) {
      message = `${this.msgInfo.getMessage(msgCode)} \n ${msg}`;
    }
    this.createToast(`${message}`, 'error');
  }
}