import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class MessageInfo {
  private msgArray: any[] = [];

  constructor(private httpClient: HttpClient) {
    this.load();
  }

  load() {
    const parent = this;
    return new Promise(function (fulfilled, rejected) {
      parent.httpClient.get('assets/message-info.json')
        .subscribe((data: any) => {
          parent.msgArray = data['message'];
          fulfilled(true);
        }, (error) => {
          rejected(error);
        });
    });
  }

  public getMessage(id: number): string {
    let msg = ' ';
    this.msgArray.forEach(function (value: any) {
      if (value.msgCode === id) {
        msg = value.msgText;
      }
    });
    return msg;
  }
}