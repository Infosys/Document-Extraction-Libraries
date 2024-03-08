:: =============================================================================================================== *
:: Copyright 2022 Infosys Ltd.                                                                                     *
:: Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at   *
:: http://www.apache.org/licenses/                                                                                 *                                                     *
:: =============================================================================================================== *

@echo off
echo Building JAR file
mvn clean package -P client
pause 