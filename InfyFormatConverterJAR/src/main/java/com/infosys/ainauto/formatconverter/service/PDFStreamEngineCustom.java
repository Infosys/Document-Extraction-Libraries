/** =============================================================================================================== *
 * Copyright 2021 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */

package com.infosys.ainauto.formatconverter.service;

import java.awt.image.BufferedImage;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.pdfbox.contentstream.PDFStreamEngine;
import org.apache.pdfbox.contentstream.operator.DrawObject;
import org.apache.pdfbox.contentstream.operator.Operator;
import org.apache.pdfbox.contentstream.operator.state.Concatenate;
import org.apache.pdfbox.contentstream.operator.state.Restore;
import org.apache.pdfbox.contentstream.operator.state.Save;
import org.apache.pdfbox.contentstream.operator.state.SetGraphicsStateParameters;
import org.apache.pdfbox.contentstream.operator.state.SetMatrix;
import org.apache.pdfbox.cos.COSBase;
import org.apache.pdfbox.cos.COSName;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.common.PDRectangle;
import org.apache.pdfbox.pdmodel.graphics.PDXObject;
import org.apache.pdfbox.pdmodel.graphics.form.PDFormXObject;
import org.apache.pdfbox.pdmodel.graphics.image.PDImageXObject;
import org.apache.pdfbox.util.Matrix;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.infosys.ainauto.formatconverter.common.CommonUtil;
import com.infosys.ainauto.formatconverter.common.Constants;
import com.infosys.ainauto.formatconverter.model.PageData;
import com.infosys.ainauto.formatconverter.model.ResourceData;
import com.infosys.ainauto.formatconverter.model.TokenData;

/**
 * Class to get images and its bbox details for a given page as input.
 */
public class PDFStreamEngineCustom extends PDFStreamEngine {

	private static final Logger LOGGER = LoggerFactory.getLogger(PDFStreamEngineCustom.class);
	private PageData pageData;
	private List<ResourceData> resourceDataList;
	private int imageCounter = 0;
	private int pageNum = -1;

	public PageData getPageData() {
		return pageData;
	}

	public List<ResourceData> getResourceDataList() {
		return resourceDataList;
	}

	/**
	 * Set's page num with index starting from 1
	 * 
	 * @param pageNum
	 */
	public void setPageNum(int pageNum) {
		this.pageNum = pageNum;
	}

	/**
	 * @throws IOException If there is an error loading text stripper properties.
	 */
	public PDFStreamEngineCustom() throws IOException {
		// preparing PDFStreamEngine
		addOperator(new Concatenate());
		addOperator(new DrawObject());
		addOperator(new SetGraphicsStateParameters());
		addOperator(new Save());
		addOperator(new Restore());
		addOperator(new SetMatrix());
	}

	@Override
	public void processPage(PDPage page) throws IOException {
		PDRectangle pageDimensions = page.getBBox();
		float pageWidth = CommonUtil.roundOff(pageDimensions.getWidth(), 4);
		float pageHeight = CommonUtil.roundOff(pageDimensions.getHeight(), 4);
		pageData = new PageData(pageNum, pageWidth, pageHeight);
		pageData.setTokenDataList(new ArrayList<TokenData>());
		resourceDataList = new ArrayList<>();

		super.processPage(page);
	}

	/**
	 * @param operator The operation to perform.
	 * @param operands The list of arguments.
	 *
	 * @throws IOException If there is an error processing the operation.
	 */
	@Override
	protected void processOperator(Operator operator, List<COSBase> operands) throws IOException {
		String operation = operator.getName();
		if ("Do".equals(operation)) {
			COSName objectName = (COSName) operands.get(0);
			PDXObject xobject = getResources().getXObject(objectName);
			String debugMessage = String.format("Page=%s | Name=%s | Type=%s", pageData.getPage(), objectName,
					xobject.getClass());
			LOGGER.debug(debugMessage);
			// check if the object is an image object
			if (xobject instanceof PDImageXObject) {
				int pageCounter = pageData.getPage();
				imageCounter++;
				String imageId = String.format("P%d_IMG%d", pageCounter, imageCounter);

				String imageFileName = "";
				PDImageXObject pdInageXObject = (PDImageXObject) xobject;
				{
					BufferedImage bufferedImage = pdInageXObject.getImage();
					String imageFormat = Constants.IMAGE_FORMAT_JPG;
					if (bufferedImage.getColorModel().hasAlpha()) {
						imageFormat = Constants.IMAGE_FORMAT_PNG;
					}
					imageFileName = imageId + "." + imageFormat;
					resourceDataList
							.add(new ResourceData(imageId, imageFileName, imageFormat, pdInageXObject.getImage()));
				}

				Matrix ctmNew = getGraphicsState().getCurrentTransformationMatrix();
				float imageXScale = ctmNew.getScalingFactorX();
				float imageYScale = ctmNew.getScalingFactorY();

				float[] bbox = { 0, 0, 0, 0 };
				// bbox format = X1,Y1,X2,Y2
				bbox[0] = ctmNew.getTranslateX();
				bbox[1] = pageData.getHeight() - ctmNew.getTranslateY();
				bbox[2] = bbox[0] + imageXScale;
				bbox[3] = bbox[1] - imageYScale;

				for (int i = 0; i < bbox.length; i++) {
					bbox[i] = CommonUtil.roundOff(bbox[i], 4);
				}

				TokenData lineTokenData = new TokenData(imageId, TokenData.TOKEN_TYPE_IMAGE, "", bbox);
				lineTokenData.setUri("file:///" + imageFileName);
				pageData.getTokenDataList().add(lineTokenData);

			} else if (xobject instanceof PDFormXObject) {
				PDFormXObject form = (PDFormXObject) xobject;
				showForm(form);
			}
		} else {
			super.processOperator(operator, operands);
		}
	}
}
