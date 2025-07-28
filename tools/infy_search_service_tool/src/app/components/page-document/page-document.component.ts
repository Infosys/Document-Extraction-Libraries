/** =============================================================================================================== *
 * Copyright 2024 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */

import { Component } from '@angular/core';
import { FormGroup, FormControl, FormArray } from '@angular/forms';
import { SearchService } from '../../services/search.service';
import { SafeResourceUrl } from '@angular/platform-browser';
import { ActivatedRoute } from '@angular/router';
import { EncodingService } from '../../services/encoding.service';
import { ToasterService } from '../../services/toaster.service';

@Component({
  selector: 'app-page-document',
  templateUrl: './page-document.component.html',
  styleUrl: './page-document.component.scss'
})
export class PageDocumentComponent {
  queryForm: FormGroup;


  constructor(private searchService: SearchService,
    private route: ActivatedRoute,private encodingService: EncodingService, private toasterService: ToasterService
  ) {
    this.queryForm = new FormGroup({
      query: new FormControl(''),
      searchServiceUrl: new FormControl(''),
      resourceServiceUrl: new FormControl(''),

      llmBaseUrl: new FormControl(''),
      llmKey: new FormControl(''),

      retrieveEnabled: new FormControl(true),
      retrieveIndexId: new FormControl(''),
      retrieverPreFilterK: new FormControl(null),
      retrieveFilterMetadata: new FormArray([]),
      retrieveTopK: new FormControl(null),
      retrieveVectorEnabled: new FormControl(true),
      retrieveSparseEnabled: new FormControl(true),
      retrieveRrfEnabled: new FormControl(true),
      retrieveCustomMetadataFilterEnabled: new FormControl(true),

      generateEnabled: new FormControl(true),
      generateModelName: new FormControl(''),
      generateDeployName: new FormControl(''),
      generateMaxTokens: new FormControl(1000),
      generateTemp: new FormControl(0.5),
      generateTopK: new FormControl(2),
      generateAttempts: new FormControl(1)
    });
  }

  model = {
    isLoading: false,
    responseObj: {} as any,
    showDetails: false,
    sources: [],
    page_num: 0,
    docUrl: '' as SafeResourceUrl,
    queryObject: {},
    queryHeaders: {},

    query: '',
    searchUrl: '',
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

    isPaneExpanded: false,
    dbName: '',
    docName: '',
    fileType: '' as any,
  }

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      let fileName = params['fileName'];
      let docName = params['docName'];

      this.model.query = params['query'];
      this.model.searchServiceUrl = params['searchServiceUrl'];
      this.model.resourceServiceUrl = params['resourceServiceUrl'];

      this.model.llmBaseUrl = params['llmBaseUrl'];
      let encodedKey = params['extraParams'];
      this.model.llmKey = this.encodingService.decode(encodedKey);

      this.model.retrieveEnabled = params['retrieveEnabled'];
      this.model.retrieveIndexId = params['retrieveIndexId'];
      this.model.retrieverPreFilterK = params['retrieverPreFilterK'];
      this.model.retrieveFilterMetadata = JSON.parse(params['retrieveFilterMetadata']);
      this.model.retrieveTopK = params['retrieveTopK'];
      this.model.retrieveVectorEnabled = params['retrieveVectorEnabled'];
      this.model.retrieveSparseEnabled = params['retrieveSparseEnabled'];
      this.model.retrieveRrfEnabled = params['retrieveRrfEnabled'];
      this.model.retrieveCustomMetadataFilterEnabled = params['retrieveCustomMetadataFilterEnabled'];

      this.model.generateModelName = params['generateModelName'];
      this.model.generateDeployName = params['generateDeployName'];

      this.fetchDocument(fileName);

      this.queryForm.get('query')?.setValue(this.model.query);
      this.queryForm.get('searchServiceUrl')?.setValue(this.model.searchServiceUrl);
      this.queryForm.get('resourceServiceUrl')?.setValue(this.model.resourceServiceUrl);

      this.queryForm.get('llmBaseUrl')?.setValue(this.model.llmBaseUrl);
      this.queryForm.get('llmKey')?.setValue(this.model.llmKey);

      this.queryForm.get('retrieveEnabled')?.setValue(this.model.retrieveEnabled);
      this.queryForm.get('retrieveIndexId')?.setValue(this.model.retrieveIndexId);
      this.queryForm.get('retrieverPreFilterK')?.setValue(this.model.retrieverPreFilterK);
      this.initializeRetrieveFilterMetadata(docName);
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
  }

  get retrieveFilterMetadata(): FormArray {
    return this.queryForm.get('retrieveFilterMetadata') as FormArray;
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

  fetchDocument(fileName: string) {
    const parent = this;
    parent.model.resourceUrl = parent.model.resourceServiceUrl.endsWith('/') ? parent.model.resourceServiceUrl.slice(0, -1) : parent.model.resourceServiceUrl;

    parent.searchService.getDocument({ file_name: fileName }, parent.model.resourceUrl).then(
      (res: ArrayBuffer) => {
        let fileType = fileName.split('.').pop();
        parent.model.fileType = fileType;
        let mimeType;

        switch (parent.model.fileType) {
          case 'pdf':
            mimeType = 'application/pdf';
            break;
          case 'jpg':
          case 'jpeg':
            mimeType = 'image/jpeg';
            break;
          case 'png':
            mimeType = 'image/png';
            break;
          case 'txt':
            mimeType = 'text/plain';
            break;
          default:
            mimeType = 'application/octet-stream';
        }

        let file = new Blob([res], { type: mimeType });
        let fileURL = URL.createObjectURL(file);
        parent.model.docUrl = fileURL;
      },
      (error: any) => {
        console.log('Error:', error);
        parent.toasterService.failure(104);
      }
    );
  }

  isImageFile(): boolean {
    return ['jpg', 'jpeg', 'png'].includes(this.model.fileType);
  }

  clearQuery(): void {
    const parent = this;
    this.queryForm.get('query')?.setValue('');
    this.queryForm.get('llmBaseUrl')?.setValue('');
    this.queryForm.get('llmKey')?.setValue('');

    this.queryForm.get('retrieveEnabled')?.setValue(true);
    this.queryForm.get('retrieveIndexId')?.setValue('');
    this.queryForm.get('retrieverPreFilterK')?.setValue(10);
    this.queryForm.get('retrieveFilterMetadata')?.setValue({});
    this.queryForm.get('retrieveTopK')?.setValue(1);
    this.queryForm.get('retrieveVectorEnabled')?.setValue(true);
    this.queryForm.get('retrieveSparseEnabled')?.setValue(true);
    this.queryForm.get('retrieveRrfEnabled')?.setValue(true);
    this.queryForm.get('retrieveCustomMetadataFilterEnabled')?.setValue(true);
    this.queryForm.get('retrieveCustomMetadataFilterModelName')?.setValue('');
    this.queryForm.get('retrieveCustomMetadataFilterDeployName')?.setValue('');

    this.queryForm.get('generateEnabled')?.setValue(true);
    this.queryForm.get('generateModelName')?.setValue('');
    this.queryForm.get('generateDeployName')?.setValue('');
    this.queryForm.get('generateMaxTokens')?.setValue(1000);
    this.queryForm.get('generateTemp')?.setValue(0);
    this.queryForm.get('generateTopK')?.setValue(1);
    this.queryForm.get('generateAttempts')?.setValue(1);
  }

  submitQuery() {
    const parent = this;
    if (!parent.validateMandatoryFields()) {
      return;
    }
    parent.model.queryObject = {
      "question": this.queryForm.value.query,
      "retrieval": {
        "enabled": this.queryForm.value.retrieveEnabled,
        "index_id": this.queryForm.value.retrieveIndexId,
        "pre_filter_fetch_k": this.queryForm.value.retrieverPreFilterK,
        "filter_metadata": {},
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
    // console.log("queryObj", parent.model.queryObject)
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
    parent.model.isLoading = true;
    try {
      parent.searchService.getQueryResponse(parent.model.queryObject, parent.model.queryHeaders, parent.model.searchUrl).then((response: any) => {
        parent.model.responseObj = response.response.answers[0]
        // console.log("responseObj", parent.model.responseObj);
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

  formatBBox(bbox: any): string {
    return Array.isArray(bbox) ? bbox.join(', ') : 'N/A';
  }

  objectKeys(obj: any): string[] {
    return Object.keys(obj);
  }

  isObject(value: any): boolean {
    return value && typeof value === 'object' && !Array.isArray(value);
  }

  isArrayType(value: any): boolean {
    return Array.isArray(value);
  }

  isObjectType(value: any): boolean {
    return value && typeof value === 'object' && !Array.isArray(value);
  }

  parseResponse(response: string) {
    try {
      const parsed = JSON.parse(response);
      if (parsed && parsed.sources) {
        this.model.sources = parsed.sources;
        this.model.page_num = this.model.sources[0]['page_no']
      }
      return parsed;
    } catch (e) {
      console.error('Failed to parse response:', e);
      return null;
    }
  }

  togglePane() {
    const parent = this;
    parent.model.isPaneExpanded = !parent.model.isPaneExpanded;
  }

}
