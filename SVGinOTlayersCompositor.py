# -*- coding: utf-8 -*-
# SVGinOT_layersCompositor by gluk 
# ver.0.21
from Tkinter import *;
import tkMessageBox;
import fontforge;
import psMat;
import xml.etree.ElementTree as ET;
import sys;
import os;
import tempfile;
import shutil;
if not hasattr(sys, 'argv'):
    sys.argv  = [''];
  
def contour2svg(layIsQuad,contour,prc):
   wyn="";
   if not layIsQuad: # Cubic Bezier Curve
      wyn+="M "+str(round(contour[0].x,prc))+" "+str(round(contour[0].y,prc));
      prev=0;
      for p in range(1,len(contour)):
         if contour[p].on_curve:
            if prev==0:
               wyn+=" L "+str(round(contour[p].x,prc))+" "+str(round(contour[p].y,prc));
            elif prev==2:
               wyn+=" C "+str(round(contour[p-2].x,prc))+" "+str(round(contour[p-2].y,prc))+" "+str(round(contour[p-1].x,prc))+" "+str(round(contour[p-1].y,prc))+" "+str(round(contour[p].x,prc))+" "+str(round(contour[p].y,prc));
            prev=0;
         else:
            prev+=1;
            if (p==len(contour)-1):
               wyn+=" C "+str(round(contour[p-1].x,prc))+" "+str(round(contour[p-1].y,prc))+" "+str(round(contour[p].x,prc))+" "+str(round(contour[p].y,prc))+" "+str(round(contour[0].x,prc))+" "+str(round(contour[0].y,prc));
      if contour.closed:
         wyn+="z";
      wyn+=" ";
   else: #quadratic Bezier Curve
      #TO DO
      return wyn;
   return wyn;

 
def SVGinOTlayComp(arg, font):
   try:
      from fontTools.ttLib import TTFont;
      import fontTools;
   except:
      tkMessageBox.showwarning("Stop","SvgOTmaker: fontTools not installed!");
      return
   precision = 2;       #precision of SVG points
   SvgOtGenVer = 0.21; #version
   SvgPaths={};
   
   # prepare dir paths file names etc.
   orgSfdName=font.path;
   orgDirName, orgFileName = os.path.split(orgSfdName);
   font.save(orgSfdName);
   
   layers=[];allLayers=[];
   for aLayer in font.layers:
      if (font.layers[aLayer].is_background != 1):
         allLayers.append(aLayer);
         if (font.layers[aLayer].is_quadratic != 1):
            layers.append(aLayer);
   if len(layers)==0:
      tkMessageBox.showwarning("Warning","no layers with qubic paths for SVG");
      return
   lb0={}; lb1={}; lb2={}; lb3={};
   opt={}; color={}; layer={}; opacity={};
   gridParam={'padx':'2', 'pady':'2', 'ipadx':'2', 'ipady':'2'};
   
   def dialogAddLayer(n,dataLayer=(layers[0],'','1.0')):
      lb0[n] = Label(window, text=str(n+1)+".");
      lb1[n] = Label(window, text="layer");
      layer[n] = StringVar(window);
      layer[n].set(dataLayer[0]); 
      opt[n] = OptionMenu(window, layer[n], *layers);
      lb2[n] = Label(window, text="color #");
      color[n] = Entry(window,width=6);
      color[n].insert(END, dataLayer[1]);
      lb3[n] = Label(window, text="opacity");
      opacity[n] = Entry(window,width=4);
      opacity[n].insert(END, dataLayer[2]);
      lb0[n].grid(column=0, row=n+3, **gridParam);
      lb1[n].grid(column=1, row=n+3, **gridParam);
      opt[n].grid(column=2, row=n+3, **gridParam);
      lb2[n].grid(column=3, row=n+3, **gridParam);
      color[n].grid(column=4, row=n+3, **gridParam);
      lb3[n].grid(column=5, row=n+3, **gridParam);
      opacity[n].grid(column=6, row=n+3, **gridParam);  
      btnA.grid(column=2, row=n+4, **gridParam);
      btnG.grid(column=2, row=n+5, **gridParam);
      btnC.grid(column=2, row=n+6, **gridParam);
      btnR.grid(column=4, row=n+6, **gridParam);
      window.layCounter+=1;
   
   def dialogGo():
      okey=True;
      SVGlayer={};
      SVGcolor={};
      SVGopacity={};
      fallbackLayer=layerF.get();
      for n in layer:
         SVGlayer[n]=layer[n].get();
      for n in color:
         tempColor=color[n].get();
         if (len(tempColor)==6 or len(tempColor)==3):
            try:
               intTempColor=int("0x"+tempColor, 16);
               if (intTempColor>0xffffff or intTempColor<0x000000):
                  okey=False;
                  tkMessageBox.showwarning("Warning","000000<= Color <=ffffff");
            except:
               okey=False;
               tkMessageBox.showwarning("Warning","Problem with Color");
         else:
            okey=False;
            tkMessageBox.showwarning("Warning","Problem with Color");
         SVGcolor[n]=color[n].get();
      for n in opacity:
         tempOpacity=opacity[n].get();
         try:
            floatTempOpacity=float(tempOpacity);
            if (floatTempOpacity>1 or floatTempOpacity<0):
               okey=False;
               tkMessageBox.showwarning("Warning","0.0 <= Opacity <=1.0");
         except:
            okey=False;
            tkMessageBox.showwarning("Warning","Problem with Opacity");
         SVGopacity[n]=tempOpacity;
      if okey:
         window.okey=True;
         window.destroy();
         window.returnData=(SvgOtGenVer,fallbackLayer,SVGlayer,SVGcolor,SVGopacity);
         if (not font.persistent):
            font.persistent={};
         font.persistent['SvgOtData']=window.returnData;

   def dialogCancelResetWindow():
      window.okey=False;
      window.destroy();
      if font.persistent and ('SvgOtData' in font.persistent):
         del font.persistent['SvgOtData'];
      window.layCounter=0;
      
   def dialogCancelWindow():
      window.okey=False;
      window.destroy();
      window.layCounter=0;
      
   window = Tk();
   window.okey=False;
   window.layCounter=0;
   window.title("SVGinOT layers Compositor");
   lbFT     = Label(window, text="Layer with 'fallback' glyphs");
   lbF      = Label(window, text="fallback");
   layerF   = StringVar(window);
   optF     = OptionMenu(window,layerF,*allLayers);
   layerF.set(allLayers[0]);
   lbST     = Label(window, text="Layers for SVG glyphs");
   btnA = Button(window, text="Add Layer", command=lambda:dialogAddLayer(window.layCounter));
   btnG = Button(window, text="Generate OpenTypeSVG font", command=dialogGo);
   btnC = Button(window, text="Cancel", command=dialogCancelWindow);
   btnR = Button(window, text="Cancel&Reset", command=dialogCancelResetWindow);
   lbFT.grid(column=2, row=0, **gridParam);
   lbF.grid (column=1, row=1, **gridParam);
   optF.grid(column=2, row=1, **gridParam);
   lbST.grid(column=2, row=2, **gridParam);   
   btnA.grid(column=2, row=3, **gridParam);
   btnG.grid(column=2, row=4, **gridParam);
   btnC.grid(column=2, row=5, **gridParam);
   btnR.grid(column=4, row=5, **gridParam);
   if font.persistent and ('SvgOtData' in font.persistent):
      (SvgOtGenVerR,fallbackLayerR,SVGlayerR,SVGcolorR,SVGopacityR)=font.persistent['SvgOtData'];
      layerF.set(fallbackLayerR);
      for i in range(len(SVGlayerR)):
         if SVGlayerR[i] in layers:
            dialogAddLayer(window.layCounter,dataLayer=(SVGlayerR[i],SVGcolorR[i],SVGopacityR[i]));
         else:
            dialogAddLayer(window.layCounter,dataLayer=(layers[0],SVGcolorR[i],SVGopacityR[i]));
            tkMessageBox.showwarning("Warning","Problem with layer: " + SVGlayerR[i]);
   else:
      dialogAddLayer(window.layCounter,dataLayer=(layers[0],'000000','1.0'));
   
   window.mainloop();

   if (not window.okey):
      window.layCounter=0;
      return;
      
   #temp directory
   tmpDirName = tempfile.mkdtemp('-tmp','svg-',orgDirName);

   #data from Tk dialog window
   (SvgOtGenVerO,fallbackLayerO,SVGlayerO,SVGcolorO,SVGopacityO)=window.returnData;
   
   #generate 'classic' ttf font
   baseFontFileName = os.path.join(tmpDirName,font.fontname+'.ttf');
   font.generate(baseFontFileName, flags=('opentype','dummy-dsig','omit-instructions'),layer=fallbackLayerO);
   
   #fontTools font
   ttLibVersion=fontTools.version;
   mTTFont = TTFont(baseFontFileName);
   baseTtxFileName = os.path.join(tmpDirName,font.fontname+'.ttx');
   mTTFont.saveXML(baseTtxFileName, splitTables=True);
   mGlyphOrder=mTTFont.getGlyphOrder();
   
   #temporary sfd file for svg glyphs
   tmpSfdFileName = os.path.join(tmpDirName,font.fontname+'-temp.sfd');
   font.save(tmpSfdFileName);
   tempFont=fontforge.open(tmpSfdFileName);
   tempFont.selection.all();
   tempFont.transform(psMat.scale(1,-1));
   #tempFont.transform(psMat.translate(0,tempFont.ascent));
   for aLayer in SVGlayerO.values():
      tempFont.activeLayer=aLayer;
      tempFont.unlinkReferences();
      pathLay={};
      for g in tempFont:
         lay=tempFont[g].layers[aLayer];
         if len(lay)>0:
            wyn="";
            for kt in lay:
               wyn+=contour2svg(lay.is_quadratic,kt,precision);
            pathLay[g]=wyn[:-1];
         else:
            pathLay[g]=False;
      SvgPaths[aLayer]=pathLay;
   SvgOutput='<?xml version="1.0" encoding="UTF-8"?>\n<ttFont ttLibVersion="'+ttLibVersion+'"><SVG>';
   for glyphNr in range(len(mGlyphOrder)):
      glyphName = mGlyphOrder[glyphNr];
      if glyphName in tempFont:
         nLay='<?xml version="1.0" encoding="utf-8"?><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.2"';
         nLay+= ' id="glyph'+str(glyphNr)+'">';
         for layerNr,aLayer in SVGlayerO.items():
            if SvgPaths[aLayer][glyphName]:
               nLay+='<path style="stroke:none;opacity:'+SVGopacityO[layerNr]+';fill:#'+SVGcolorO[layerNr]+';"';
               nLay+=' d="'+SvgPaths[aLayer][glyphName]+'" />';
         nLay+='</svg>';
         SvgOutput+='<svgDoc endGlyphID="'+str(glyphNr)+'" startGlyphID="'+str(glyphNr)+'"><![CDATA[';
         SvgOutput+=nLay;
         SvgOutput+=']]></svgDoc>';
   SvgOutput+='</SVG></ttFont>';
   svgTtxFileName = os.path.join(tmpDirName,font.fontname+'.S_V_G_.ttx');
   fil=open(svgTtxFileName, 'a' );
   fil.write(SvgOutput);
   fil.close();
   
   #modify base ttx file
   tree = ET.parse(baseTtxFileName)
   root = tree.getroot()
   svgTtxOnlyFileName = font.fontname+'.S_V_G_.ttx';
   ET.SubElement(root, 'SVG', attrib={'src':svgTtxOnlyFileName})
   tree.write(baseTtxFileName, encoding="UTF-8", xml_declaration=True, method="xml")
   
   #fontTools NEW color font
   newmTTFont = TTFont();
   newmTTFont.importXML(baseTtxFileName);
   colorFontFileName = os.path.join(orgDirName,font.fontname+'Color.ttf');
   newmTTFont.save(colorFontFileName);
   
   # cleaning
   fontforge.open(orgSfdName);
   tempFont.close();
   shutil.rmtree(tmpDirName);
   window.layCounter=0;
   
fontforge.registerMenuItem(SVGinOTlayComp,None,None,"Font",None,"SVGinOpenType","layersCompositor 0.21");
