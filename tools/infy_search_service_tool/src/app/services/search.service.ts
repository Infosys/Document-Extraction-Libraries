/** =============================================================================================================== *
 * Copyright 2024 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */

import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class SearchService {

  constructor(private httpClient: HttpClient,) { }

  getQueryResponse(queryObject: any, queryHeaders: any, searchUrl: any) {
    const parent = this;
    const requestOptions = {
      headers: new HttpHeaders(queryHeaders),
    };
    const url = searchUrl + '/api/v1/inference/search';
    return new Promise((fulfilled, rejected) => {
      parent.httpClient.post(url, queryObject, requestOptions).subscribe({
        next: (response: any) => {
          if (response.responseCde!= 200) {
            rejected(response)
          } else {
            fulfilled(response);
          }
        },
        error: (_error) => {
          rejected(_error);
        }
      });
    });
  }

  getDocument(docObject: any, resourceServiceUrl: string): Promise<ArrayBuffer> {
    const url = `${resourceServiceUrl}/api/v1/resource/fetch_file`;
    const headers = new HttpHeaders({
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    });

    const body = {
      resource_file_name: docObject.file_name
    };

    return new Promise((fulfilled, rejected) => {
      this.httpClient.post(url, body, { headers, responseType: 'arraybuffer' }).subscribe({
        next: (response: ArrayBuffer) => {
          fulfilled(response);
        },
        error: (error: any) => {
          rejected(error);
        }
      });
    });
  }

}