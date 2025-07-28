/** =============================================================================================================== *
 * Copyright 2024 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */

import { Injectable } from '@angular/core';

@Injectable({
    providedIn: 'root'
})
export class EncodingService {
    encode(value: string): string {
        return btoa(value); 
    }

    decode(value: string): string {
        try {
            return atob(value);
        } catch (error) {
            // console.error('Error decoding value:', error);
            return '';
        }
    }
}