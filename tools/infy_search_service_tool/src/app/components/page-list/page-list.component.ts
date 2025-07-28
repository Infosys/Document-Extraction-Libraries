/** =============================================================================================================== *
 * Copyright 2024 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */

import { Component, Query } from '@angular/core';
import { FormGroup, FormControl, FormArray, Validators } from '@angular/forms';
import { SearchService } from '../../services/search.service';
import { EncodingService } from '../../services/encoding.service';
import { ActivatedRoute } from '@angular/router';
import { ToasterService } from '../../services/toaster.service';

@Component({
  selector: 'app-page-list',
  templateUrl: './page-list.component.html',
  styleUrl: './page-list.component.scss'
})
export class PageListComponent {
  queryForm: FormGroup;

  constructor(
    private searchService: SearchService, private encodingService: EncodingService, private route: ActivatedRoute, private toasterService: ToasterService) {
    this.queryForm = new FormGroup({
      query: new FormControl(''),
      searchServiceUrl: new FormControl(''),
      resourceServiceUrl: new FormControl(''),

      llmBaseUrl: new FormControl(''),
      llmKey: new FormControl(''),

      retrieveEnabled: new FormControl(true),
      retrieveIndexId: new FormControl(''),
      retrieverPreFilterK: new FormControl(10),
      retrieveFilterMetadata: new FormArray([]),
      retrieveTopK: new FormControl(5),
      retrieveVectorEnabled: new FormControl(true),
      retrieveSparseEnabled: new FormControl(true),
      retrieveRrfEnabled: new FormControl(true),
      retrieveCustomMetadataFilterEnabled: new FormControl(true),

      generateEnabled: new FormControl(false),
      generateModelName: new FormControl(''),
      generateDeployName: new FormControl(''),
      generateMaxTokens: new FormControl(1000),
      generateTemp: new FormControl(0),
      generateTopK: new FormControl(2),
      generateAttempts: new FormControl(1)
    });
  }

  model = {
    isLoading: false,
    responseObj: {} as any,
    sources: [],
    page_num: 0,
    bbox_items: [],
    isContentExpanded: false,
    queryObject: {},
    queryHeaders: {},
    searchUrl: '',
    isPaneExpanded: true,
    appVersion: '',

    query: '',
    searchServiceUrl: '',
    resourceUrl: '',
    resourceServiceUrl: '',

    llmBaseUrl: '',
    llmKey: '',

    retrieveEnabled: true,
    retrieveIndexId: '',
    retrieverPreFilterK: 10,
    retrieveFilterMetadata: {},
    retrieveTopK: 0,
    retrieveVectorEnabled: true,
    retrieveSparseEnabled: true,
    retrieveRrfEnabled: true,
    retrieveCustomMetadataFilterEnabled: true,

    generateEnabled: false,
    generateModelName: '',
    generateDeployName: '',
  }

  ngOnInit() {
    const parent = this;
    this.route.queryParams.subscribe(params => {
      let fileName = params['fileName'];
      let docName = params['docName'];

      this.model.query = params['query'];
      this.model.searchServiceUrl = params['searchServiceUrl'];
      this.model.resourceServiceUrl = params['resourceServiceUrl'];

      this.model.llmBaseUrl = params['llmBaseUrl'];
      if (params['extraParams']) {
        try {
          let encodedKey = params['extraParams'];
          this.model.llmKey = this.encodingService.decode(encodedKey);
        } catch (error) {
          this.model.llmKey = ''; 
        }
      } else {
        this.model.llmKey = ''; 
      }

      this.model.retrieveEnabled = params['retrieveEnabled'];
      this.model.retrieveIndexId = params['retrieveIndexId'];
      this.model.retrieverPreFilterK = params['retrieverPreFilterK'];
      if (params['retrieveFilterMetadata']) {
        this.model.retrieveFilterMetadata = JSON.parse(params['retrieveFilterMetadata']);
      }
      this.model.retrieveTopK = params['retrieveTopK'];
      this.model.retrieveVectorEnabled = params['retrieveVectorEnabled'];
      this.model.retrieveSparseEnabled = params['retrieveSparseEnabled'];
      this.model.retrieveRrfEnabled = params['retrieveRrfEnabled'];
      this.model.retrieveCustomMetadataFilterEnabled = params['retrieveCustomMetadataFilterEnabled'];

      this.model.generateModelName = params['generateModelName'];
      this.model.generateDeployName = params['generateDeployName'];

      this.queryForm.get('query')?.setValue(this.model.query);
      this.queryForm.get('searchServiceUrl')?.setValue(this.model.searchServiceUrl);
      this.queryForm.get('resourceServiceUrl')?.setValue(this.model.resourceServiceUrl);

      this.queryForm.get('llmBaseUrl')?.setValue(this.model.llmBaseUrl);
      this.queryForm.get('llmKey')?.setValue(this.model.llmKey);

      this.queryForm.get('retrieveEnabled')?.setValue(this.model.retrieveEnabled);
      this.queryForm.get('retrieveIndexId')?.setValue(this.model.retrieveIndexId);
      this.queryForm.get('retrieverPreFilterK')?.setValue(this.model.retrieverPreFilterK);
      // this.initializeRetrieveFilterMetadata(docName);
      this.queryForm.get('retrieveTopK')?.setValue(this.model.retrieveTopK);
      this.queryForm.get('retrieveVectorEnabled')?.setValue(this.model.retrieveVectorEnabled);
      this.queryForm.get('retrieveSparseEnabled')?.setValue(this.model.retrieveSparseEnabled);
      this.queryForm.get('retrieveRrfEnabled')?.setValue(this.model.retrieveRrfEnabled);
      this.queryForm.get('retrieveCustomMetadataFilterEnabled')?.setValue(this.model.retrieveCustomMetadataFilterEnabled);

      this.queryForm.get('generateEnabled')?.setValue(true);
      this.queryForm.get('generateModelName')?.setValue(this.model.generateModelName);
      this.queryForm.get('generateDeployName')?.setValue(this.model.generateDeployName);
      // console.log('queryform', this.queryForm)
    });
    parent.addMetadataField();
  }

  get retrieveFilterMetadata(): FormArray {
    return this.queryForm.get('retrieveFilterMetadata') as FormArray;
  }

  addMetadataField(event?: Event): void {
    if (event) {
      event.stopPropagation();
    }
    this.retrieveFilterMetadata.push(new FormGroup({
      key: new FormControl(''),
      value: new FormControl('')
    }));
  }

  removeMetadataField(index: number, event?: Event): void {
    if (event) {
      event.stopPropagation();
    }
    this.retrieveFilterMetadata.removeAt(index);
  }

  initializeRetrieveFilterMetadata(docName: string): void {
    const metadata = this.model.retrieveFilterMetadata as { [key: string]: string };
    for (const key in metadata) {
      if (metadata.hasOwnProperty(key)) {
        const cleanKey = key.replace(/"/g, '');
        this.retrieveFilterMetadata.push(new FormGroup({
          key: new FormControl(cleanKey),
          value: new FormControl(metadata[key])
        }));
      }
    }
    this.retrieveFilterMetadata.push(new FormGroup({
      key: new FormControl('docName'),
      value: new FormControl(docName)
    }));
  }

  clearForm(): void {
    const parent = this;
    this.queryForm.get('query')?.setValue('');
    // this.queryForm.get('searchServiceUrl')?.setValue('');
    // this.queryForm.get('resourceServiceUrl')?.setValue('');
    // this.queryForm.get('llmBaseUrl')?.setValue('');
    // this.queryForm.get('llmKey')?.setValue('');

    // this.queryForm.get('retrieveEnabled')?.setValue(true);z
    // this.queryForm.get('retrieveIndexId')?.setValue('');
    // this.queryForm.get('retrieverPreFilterK')?.setValue(10);
    // this.retrieveFilterMetadata.clear();
    // this.addMetadataField();
    // this.queryForm.get('retrieveTopK')?.setValue(1);
    // this.queryForm.get('retrieveVectorEnabled')?.setValue(true);
    // this.queryForm.get('retrieveSparseEnabled')?.setValue(true);
    // this.queryForm.get('retrieveRrfEnabled')?.setValue(true);
    // this.queryForm.get('retrieveCustomMetadataFilterEnabled')?.setValue(true);
    // this.queryForm.get('retrieveCustomMetadataFilterModelName')?.setValue('');
    // this.queryForm.get('retrieveCustomMetadataFilterDeployName')?.setValue('');

    // this.queryForm.get('generateEnabled')?.setValue(false);
    // this.queryForm.get('generateModelName')?.setValue('');
    // this.queryForm.get('generateDeployName')?.setValue('');
    // this.queryForm.get('generateMaxTokens')?.setValue(1000);
    // this.queryForm.get('generateTemp')?.setValue(0);
    // this.queryForm.get('generateTopK')?.setValue(1);
    // this.queryForm.get('generateAttempts')?.setValue(1);
    parent.model.queryObject = {};
    parent.model.responseObj = {};
    if (!parent.model.isPaneExpanded) {
      parent.model.isPaneExpanded = true;
    }

  }

  parseFilteredMetadata(metadataArray: any[]):any{
    return metadataArray.reduce((acc: any, item: any) => {
      if (item.key && item.value) {
        acc[`"${item.key}"`] = item.value;
      }
      return acc;
    }, {});
  }
  
  submitQuery() {
    const parent = this;
    if (!parent.validateMandatoryFields()) {
      return;
    }
    const metadata = parent.parseFilteredMetadata(this.retrieveFilterMetadata.value);

    parent.model.queryObject = {
      "question": this.queryForm.value.query,
      "retrieval": {
        "enabled": this.queryForm.value.retrieveEnabled,
        "index_id": this.queryForm.value.retrieveIndexId,
        "pre_filter_fetch_k": this.queryForm.value.retrieverPreFilterK,
        "filter_metadata": metadata,
        "top_k": this.queryForm.value.retrieveTopK,
        "datasource": {
          "vectorindex": {
            "enabled": this.queryForm.value.retrieveVectorEnabled
          },
          "sparseindex": {
            "enabled": this.queryForm.value.retrieveSparseEnabled
          }
        },
        "hybrid_search": {
          "rrf": {
            "enabled": this.queryForm.value.retrieveRrfEnabled
          }
        },
        "custom_metadata_filter": {
          "enabled": this.queryForm.value.retrieveCustomMetadataFilterEnabled,
          "model_name": this.queryForm.value.generateModelName,
          "deployment_name": this.queryForm.value.generateDeployName
        }
      },
      "generation": {
        "enabled": this.queryForm.value.generateEnabled,
        "model_name": this.queryForm.value.generateModelName,
        "deployment_name": this.queryForm.value.generateDeployName,
        "max_tokens": this.queryForm.value.generateMaxTokens,
        "temperature": this.queryForm.value.generateTemp,
        "top_k_used": this.queryForm.value.generateTopK,
        "total_attempts": this.queryForm.value.generateAttempts
      }
    }
    // console.log("queryobj", parent.model.queryObject)
    parent.model.isLoading = true;
    parent.model.queryHeaders = {
      'accept': 'application/json',
      'api-endpoint': this.queryForm.value.llmBaseUrl,
      'api-key': this.queryForm.value.llmKey,
      'Content-Type': 'application/json'
    };
    if (this.queryForm.value.searchServiceUrl.endsWith('/')) {
      parent.model.searchUrl = this.queryForm.value.searchServiceUrl.slice(0, -1);
    }
    else {
      parent.model.searchUrl = this.queryForm.value.searchServiceUrl;
    }
    // console.log("headersobj", parent.model.queryHeaders)
    try {
      parent.searchService.getQueryResponse(parent.model.queryObject, parent.model.queryHeaders, parent.model.searchUrl).then((response: any) => {
        parent.model.responseObj = response.response.answers[0]
        // console.log("responseobj", parent.model.responseObj);
        // this.toasterService.success(101);
        parent.model.isLoading = false;
      }).catch((error: any) => {
        console.error("Error response:", error);
        let errorMessage = error.responseMsg || 'Error occurred while fetching the response.';
        parent.toasterService.failureWithMessage(errorMessage, 102);
        parent.model.isLoading = false;
      });
    } catch (error:any) {
      console.error("Error:", error);
      let errorMessage = error.responseMsg || 'Error occurred while fetching the response.';
      parent.toasterService.failureWithMessage(errorMessage, 102);
      parent.model.isLoading = false;
    }

    if (parent.model.isPaneExpanded) {
      parent.model.isPaneExpanded = false;
    }
  }

  private validateMandatoryFields(): boolean {
    if (!this.queryForm.value.query) {
      this.toasterService.failureWithMessage('Please provide a valid question.', 103);
      return false;
    }
    if (!this.queryForm.value.retrieveIndexId) {
      this.toasterService.failureWithMessage('Please provide a valid Index Id.', 103);
      return false;
    }
    if (!this.queryForm.value.llmBaseUrl) {
      this.toasterService.failureWithMessage('Please provide a valid llm base url.', 103);
      return false;
    }
    if (!this.queryForm.value.llmKey) {
      this.toasterService.failureWithMessage('Please provide a valid llm key.', 103);
      return false;
    }
    if (!this.queryForm.value.searchServiceUrl) {
      this.toasterService.failureWithMessage('Please provide a valid DEL Search service base endpoint.', 103);
      return false;
    }
    if (!this.queryForm.value.retrieveVectorEnabled && !this.queryForm.value.retrieveSparseEnabled) {
      this.toasterService.failureWithMessage('Please enable atleast one of vector or sparse index.', 103);
      return false;
    }
    return true;
  }

  getFilteredResults() {
    const parent = this;
    const responseObj = parent.model.responseObj;
    const topKList = responseObj.top_k_list || [];
    const vectorEnabled = this.queryForm.value.retrieveVectorEnabled;
    const sparseEnabled = this.queryForm.value.retrieveSparseEnabled;
    const rrfEnabled = this.queryForm.value.retrieveRrfEnabled;

    let filteredResults = [];

    if (rrfEnabled) {
      if (vectorEnabled && sparseEnabled) {
        filteredResults = topKList.flatMap((item: any) => item.rrf || []);
      } else if (vectorEnabled) {
        filteredResults = topKList.flatMap((item: any) => item.vectordb || []);
      } else if (sparseEnabled) {
        filteredResults = topKList.flatMap((item: any) => item.sparseindex || []);
      }
      else {
        console.warn('Both vector and sparse index has to be enabled when RRF is enabled.');
        return [];
      }
    } else {
      if (vectorEnabled && sparseEnabled) {
        filteredResults = topKList.flatMap((item: any) => item.vectordb || []);
      } else if (vectorEnabled) {
        filteredResults = topKList.flatMap((item: any) => item.vectordb || []);
      } else if (sparseEnabled) {
        filteredResults = topKList.flatMap((item: any) => item.sparseindex || []);
      } else {
        console.warn('No index selected.');
        return [];
      }
    }
    // console.log('filteredResults', filteredResults);
    return filteredResults;
  }

  toggleExpandContent(item: any) {
    item.isContentExpanded = !item.isContentExpanded;
  }

  togglePane() {
    const parent = this;
    parent.model.isPaneExpanded = !parent.model.isPaneExpanded;
  }

  getKeys(obj: any): string[] {
    return Object.keys(obj);
  }

  getBaseHref(): string {
    const baseElements = document.getElementsByTagName('base');
    if (baseElements.length > 0) {
      return baseElements[0].getAttribute('href') || '/';
    }
    return '/';
  }

  constructUrl(file_name: string, formcontrol: any, docName: string): string {
    const parent = this;
    const metadata = JSON.stringify(parent.parseFilteredMetadata(this.retrieveFilterMetadata.value));
    let encodedKey = parent.encodingService.encode(formcontrol.llmKey);

    let fileName = file_name.split('/').pop();
    let baseUrl = window.location.protocol + '//' + window.location.host + this.getBaseHref();
    let url = baseUrl + '/#/document?fileName=' + fileName +
      '&docName=' + docName +
      '&retrieveIndexId=' + formcontrol.retrieveIndexId +
      '&query=' + formcontrol.query +
      '&searchServiceUrl=' + formcontrol.searchServiceUrl +
      '&llmBaseUrl=' + formcontrol.llmBaseUrl +
      '&generateModelName=' + formcontrol.generateModelName +
      '&generateDeployName=' + formcontrol.generateDeployName +
      '&retrieveFilterMetadata=' + metadata +
      '&extraParams=' + encodedKey +
      '&retrieveVectorEnabled=' + formcontrol.retrieveVectorEnabled +
      '&retrieveSparseEnabled=' + formcontrol.retrieveSparseEnabled +
      '&retrieveRrfEnabled=' + formcontrol.retrieveRrfEnabled +
      '&retrieveTopK=' + formcontrol.retrieveTopK +
      '&retrieverPreFilterK=' + formcontrol.retrieverPreFilterK +
      '&resourceServiceUrl=' + formcontrol.resourceServiceUrl;
    return url;
  }

  redirectToDocView(file_name: string, formcontrol: any, doc_name: string) {
    let url = this.constructUrl(file_name, formcontrol, doc_name);
    window.open(url, '_blank');
  }
}
