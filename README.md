# SVGinOT layers Compositor
python 2.x script for FontForge. My first SVGinOpenType color fonts generator. Hope, will work...
 
# How to install:
 - install *fontTools* (3.x) for Python 2
 - place *SVGinOTlayersCompositor.py* in *~/.FontForge/python*

# How to test:
1. open *DigitaltT.sfd* (in *SVGinOTlayersCompositor_021/fontTester/* directory) in FontForge
2. from menu *Tools → SVGinOpenType → select layersCompositor 0.21*
3. layersCompositor should have previously saved layer values (and schould look like on image in doc/howto.pdf)
4. click **"Generate OpenTypeSVG font"** Button
5. in *DigitaltT.sfd* directory will be generated **DigitaltTColor.ttf**
6. open *test_in_firefox_or_edge.html* in Firefox Browser to test font  
7. play with layer values in dialog, and have hun :)

# How to made new color font:
1. open new font in FontForge
2. prepare layers:
 - you need one "fallback" layer with (at best quadratic paths) glyphs for programs without SVGinOT support
 - as many qubic layers, as you need for SVG glyphs
3. prepare glyphs ( I know..)
4. save .sfd file
4. from menu *Tools → SVGinOpenType →* select *layersCompositor 0.21*
5. select fallback layer 
6. select one SVG layer (lowest layer in your layers order) and edit color/opacity values
7. click "add new layer" for next SVG layers (reverse order!), select layers name and edit color/opacity values 
8. click **"Generate OpenTypeSVG font"** Button
9. in your .sfd directory  will be generated font *xxxxxxColor.ttf*

