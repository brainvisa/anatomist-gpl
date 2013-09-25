<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS><TS version="2.0" language="en" sourcelanguage="">
<context>
    <name>ControlledWindow</name>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/foldsplit.py" line="442"/>
        <source>SplitFoldControl</source>
        <translation>&lt;html&gt;&lt;div align=&quot;center&quot;&gt;&lt;b&gt;Split Fold Control:&lt;/b&gt;&lt;/div&gt;
&lt;p&gt;
manually or semi-manually split cortical folds in a graph.
&lt;tabe&gt;&lt;tr&gt;
&lt;td&gt;Left click:&lt;/td&gt;&lt;td&gt;prepare a cut with a single point on a fold node&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;ctrl&amp;&amp;gt;+Left click :&lt;/td&gt;&lt;td&gt;set a cut control point in a series for a dotted line cut&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;S&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;show cut line, or confirm split if the cut line is already visible&lt;/td&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;ESC&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;cancel spliit, erase control points and proposed split line&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;ctrl&amp;&amp;gt;+Right click :&lt;/td&gt;&lt;td&gt;automatically subdivize a node in several pieces&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;shift&amp;&amp;gt;+Right click :&lt;/td&gt;&lt;td&gt;automatically subdivize the entire graph by splitting large nodes&lt;/td&gt;&lt;/tr&gt;
&lt;/table&gt;&lt;tr/&gt;
Classical rotation, translation and zoom controls also apply.&lt;/p&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/selection.py" line="519"/>
        <source>SelectionControl</source>
        <translation>&lt;html&gt;&lt;div align=&quot;center&quot;&gt;&lt;b&gt;Selection&lt;/b&gt;&lt;/div&gt;
&lt;table&gt;&lt;tr&gt;
&lt;td&gt;Left btn:&lt;/td&gt;&lt;td&gt;selection&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;+ &amp;&amp;lt;shift&amp;&amp;gt;:&lt;/td&gt;&lt;td&gt;additive selection&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;+ &amp;&amp;lt;ctrl&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;toggle selection&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;Mid btn:&lt;/td&gt;&lt;td&gt;rotation&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;+ &amp;&amp;lt;shift&amp;&amp;gt;/ wheel :&lt;/td&gt;&lt;td&gt;zoom/distance&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;+ &amp;&amp;lt;ctrl&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;translation&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;Right btn:&lt;/td&gt;&lt;td&gt;menu&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;ctrl+W&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;close window&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;F9&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;full screen&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;F10&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;show/hide menus/buttons&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;S&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;synchro views&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;ctrl+C&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;set centre of view&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;alt+C&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;show position of the center of view&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;ctrl+A&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;select/unselect all objects&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;DEL&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;remove selected object from this view&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;ctrl+DEL&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;remove selected objects from group&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td colspan=&quot;2&quot;&gt;Labeling, graphs, and sulci:&lt;/td&gt;&lt;td&gt;&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;SPACE&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;pick selection label&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;ctrl&amp;&amp;gt;+&amp;&amp;lt;RETURN&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;set current label to selected objects&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;A&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;show / hide graphs labels as 3D annotations&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td colspan=&quot;2&quot;&gt;Slice movie:&lt;/td&gt;&lt;/td&gt;&lt;td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;PgUp&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;previous slice&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;PgDown&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;next slice&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;shift+PgUp&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;previous time&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;shift+PgDown&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;next time&lt;/td&gt;&lt;/tr&gt;
&lt;/table&gt;&lt;br/&gt;
Additional settings for edges selection in the toolbox GUI.&lt;/html&gt;</translation>
    </message>
</context>
<context>
    <name>Form</name>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/modelGraphs.ui" line="25"/>
        <source>Configuration</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/modelGraphs.ui" line="31"/>
        <source>Affichage</source>
        <translation type="unfinished"></translation>
    </message>
    <message encoding="UTF-8">
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/modelGraphs.ui" line="41"/>
        <source>Données :</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/modelGraphs.ui" line="51"/>
        <source>Type :</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/modelGraphs.ui" line="66"/>
        <source>raw</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/modelGraphs.ui" line="71"/>
        <source>mean</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/modelGraphs.ui" line="76"/>
        <source>bad</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/modelGraphs.ui" line="81"/>
        <source>good</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/modelGraphs.ui" line="90"/>
        <source>sillons seulements</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/modelGraphs.ui" line="95"/>
        <source>sillons + relations</source>
        <translation type="unfinished"></translation>
    </message>
    <message encoding="UTF-8">
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/modelGraphs.ui" line="109"/>
        <source>Différences absolues</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/modelGraphs.ui" line="184"/>
        <source>Fermer</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/modelGraphs.ui" line="191"/>
        <source>Appliquer</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>GradientObjectParamSelect</name>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/gradientpalette.py" line="120"/>
        <source>Save palette image...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/gradientpalette.py" line="121"/>
        <source>Edit gradient information</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/gradientpalette.py" line="122"/>
        <source>Keep as static palette</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/gradientpalette.py" line="127"/>
        <source>RGB mode</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/gradientpalette.py" line="128"/>
        <source>HSV mode</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/gradientpalette.py" line="266"/>
        <source>Gradient definition:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/gradientpalette.py" line="296"/>
        <source>Palette name:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/gradientpalette.py" line="276"/>
        <source>OK</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/gradientpalette.py" line="277"/>
        <source>Cancel</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>SelectionParameters</name>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/selection-qt4.ui" line="14"/>
        <source>Form1</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/selection-qt4.ui" line="20"/>
        <source>Edge selection:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/selection-qt4.ui" line="34"/>
        <source>Edges display mode:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/selection-qt4.ui" line="59"/>
        <source>Opacity:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/selection-qt4.ui" line="73"/>
        <source>Nodes</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/selection-qt4.ui" line="139"/>
        <source>100</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/selection-qt4.ui" line="116"/>
        <source>Edges</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/selection-qt4.ui" line="154"/>
        <source>Box highlight:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/selection-qt4.ui" line="166"/>
        <source>Use box highlighting for selection</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/selection-qt4.ui" line="179"/>
        <source>Use one box per selected object</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/selection-qt4.ui" line="188"/>
        <source>Box color: </source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/selection-qt4.ui" line="196"/>
        <source>Gray</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/selection-qt4.ui" line="201"/>
        <source>As selection</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/selection-qt4.ui" line="206"/>
        <source>Custom</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/selection-qt4.ui" line="218"/>
        <source>Custom box color: </source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/branches/4.4/shared/python_plugins/selection-qt4.ui" line="231"/>
        <source>...</source>
        <translation type="unfinished"></translation>
    </message>
</context>
</TS>
