/** =============================================================================================================== *
 * Copyright 2024 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */

import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  constructor(private http: HttpClient) {
  }

  model = {
    appVersion: ''
  }

  ngOnInit() {
    const parent = this;
    parent.http.get<{ config: { app_version: string } }>('assets/config-data.json')
      .subscribe(data => {
        parent.model.appVersion = data.config.app_version;
      });
  }
}