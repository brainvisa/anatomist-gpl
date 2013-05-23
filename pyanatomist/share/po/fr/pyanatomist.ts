<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.0" language="fr_FR">
<context>
    <name>ControlledWindow</name>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/foldsplit.py" line="416"/>
        <source>SplitFoldControl</source>
        <translation>&lt;html&gt;&lt;div align=&quot;center&quot;&gt;&lt;b&gt;Contrôle de découpe de sillons:&lt;/b&gt;&lt;/div&gt;
&lt;p&gt;Découpe manuellement ou semi-manuellement des noeuds de graphe cortical.&lt;/p&gt;
&lt;p&gt;
&lt;tabe&gt;&lt;tr&gt;
&lt;td&gt;Left click:&lt;/td&gt;&lt;td&gt;prepare a cut with a single point on a fold node&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;ctrl&amp;&amp;gt;+Left click :&lt;/td&gt;&lt;td&gt;set a cut control point in a series for a dotted line cut&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;S&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;show cut line, or confirm split if the cut line is already visible&lt;/td&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;ESC&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;cancel spliit, erase control points and proposed split line&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;ctrl&amp;&amp;gt;+Right click :&lt;/td&gt;&lt;td&gt;automatically subdivize a node in several pieces&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;shift&amp;&amp;gt;+Right click :&lt;/td&gt;&lt;td&gt;automatically subdivize the entire graph by splitting large nodes&lt;/td&gt;&lt;/tr&gt;
&lt;/table&gt;
&lt;/p&gt;
&lt;p&gt;Les contrôles classiques de rotation, translation et zoom fonctionnent aussi.&lt;/p&gt;
&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/selection.py" line="518"/>
        <source>SelectionControl</source>
        <translation>&lt;html&gt;&lt;div align=&quot;center&quot;&gt;&lt;b&gt;Sélection&lt;/b&gt;&lt;/div&gt;
&lt;p&gt;
&lt;table&gt;&lt;tr&gt;
&lt;td&gt;Btn gauche:&lt;/td&gt;&lt;td&gt;sélection&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;+ &amp;&amp;lt;shift&amp;&amp;gt;:&lt;/td&gt;&lt;td&gt;sélection additive&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;+ &amp;&amp;lt;ctrl&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;modif. sélection&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;Btn milieu:&lt;/td&gt;&lt;td&gt;rotation&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;+ &amp;&amp;lt;shift&amp;&amp;gt;/ molette :&lt;/td&gt;&lt;td&gt;zoom/distance&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;+ &amp;&amp;lt;ctrl&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;translation&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;Btn droit:&lt;/td&gt;&lt;td&gt;menu&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;ctrl+W&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;fermer la fenêtre&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;F9&amp;&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;plein écran&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;F10&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;montre/cache les menus/boutons&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;S&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;synchro vues&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;ctrl+C&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;fixe le centre de vue&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;alt+C&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;affiche la position du centre de vue&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;ctrl+A&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;sélectionne/désélectionne tous les objets&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;DEL&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;enlève les objets sélectionnés de la vue&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;ctrl+DEL&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;enlève les objets sélectionnés du groupe&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td colspan=&quot;2&quot;&gt;&lt;b&gt;Labels, graphes, et sillons:&lt;/b&gt;&lt;/td&gt;&lt;td&gt;&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;SPACE&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;&quot;pipette&quot;, mémorise le label des objets sélectionnés&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;ctrl+RETURN&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;applique le label courant aux objets sélectionnés&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;A&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;affiche / cache les labels de graphes (annotations 3D)&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td colspan=&quot;2&quot;&gt;&lt;b&gt;Défilement des coupes:&lt;/b&gt;&lt;/td&gt;&lt;/td&gt;&lt;td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;PgUp&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;coupe précédente&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;PgDown&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;coupe suivante&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;shift+PgUp&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;temps précédent&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td&gt;&amp;&amp;lt;shift+PgDown&amp;&amp;gt; :&lt;/td&gt;&lt;td&gt;temps suivant&lt;/td&gt;&lt;/tr&gt;
&lt;/table&gt;&lt;br/&gt;
&lt;/p&gt;
&lt;p&gt;
Des options supplémentaires sont disponibles dans l&apos;interface &quot;toolbox&quot; pour la sélection des relations.
&lt;/p&gt;
&lt;/html&gt;</translation>
    </message>
</context>
<context>
    <name>Form</name>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/modelGraphs.ui" line="25"/>
        <source>Configuration</source>
        <translation>Configuration</translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/modelGraphs.ui" line="31"/>
        <source>Affichage</source>
        <translation type="unfinished"></translation>
    </message>
    <message utf8="true">
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/modelGraphs.ui" line="41"/>
        <source>Données :</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/modelGraphs.ui" line="51"/>
        <source>Type :</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/modelGraphs.ui" line="66"/>
        <source>raw</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/modelGraphs.ui" line="71"/>
        <source>mean</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/modelGraphs.ui" line="76"/>
        <source>bad</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/modelGraphs.ui" line="81"/>
        <source>good</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/modelGraphs.ui" line="90"/>
        <source>sillons seulements</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/modelGraphs.ui" line="95"/>
        <source>sillons + relations</source>
        <translation type="unfinished"></translation>
    </message>
    <message utf8="true">
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/modelGraphs.ui" line="109"/>
        <source>Différences absolues</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/modelGraphs.ui" line="184"/>
        <source>Fermer</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/modelGraphs.ui" line="191"/>
        <source>Appliquer</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>GradientObjectParamSelect</name>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/gradientpalette.py" line="112"/>
        <source>Save palette image...</source>
        <translation>Sauver la palette comme image...</translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/gradientpalette.py" line="113"/>
        <source>Edit gradient information</source>
        <translation>Editer les informations de gradient</translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/gradientpalette.py" line="114"/>
        <source>Keep as static palette</source>
        <translation>Garder comme palette statique</translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/gradientpalette.py" line="119"/>
        <source>RGB mode</source>
        <translation>mode RVB</translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/gradientpalette.py" line="120"/>
        <source>HSV mode</source>
        <translation>mode HSV</translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/gradientpalette.py" line="255"/>
        <source>Gradient definition:</source>
        <translation>Définition de gradient:</translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/gradientpalette.py" line="277"/>
        <source>Palette name:</source>
        <translation>Nom de palette:</translation>
    </message>
</context>
<context>
    <name>SelectionParameters</name>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/selection-qt4.ui" line="14"/>
        <source>Form1</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/selection-qt4.ui" line="20"/>
        <source>Edge selection:</source>
        <translation>Sélection des relations:</translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/selection-qt4.ui" line="34"/>
        <source>Edges display mode:</source>
        <translation>Mode de visu des relations:</translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/selection-qt4.ui" line="59"/>
        <source>Opacity:</source>
        <translation>Opacité:</translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/selection-qt4.ui" line="73"/>
        <source>Nodes</source>
        <translation>Noeuds</translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/selection-qt4.ui" line="139"/>
        <source>100</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/selection-qt4.ui" line="116"/>
        <source>Edges</source>
        <translation>Relations</translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/selection-qt4.ui" line="154"/>
        <source>Box highlight:</source>
        <translation>Visualisation boîtes:</translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/selection-qt4.ui" line="166"/>
        <source>Use box highlighting for selection</source>
        <translation>Utiliser des boîtes pour la sélection</translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/selection-qt4.ui" line="179"/>
        <source>Use one box per selected object</source>
        <translation>Une boîte par objet sélectionné</translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/selection-qt4.ui" line="188"/>
        <source>Box color: </source>
        <translation>Couleur de boîte:</translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/selection-qt4.ui" line="196"/>
        <source>Gray</source>
        <translation>Gris</translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/selection-qt4.ui" line="201"/>
        <source>As selection</source>
        <translation>Comme sélection</translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/selection-qt4.ui" line="206"/>
        <source>Custom</source>
        <translation>Spécifique</translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/selection-qt4.ui" line="218"/>
        <source>Custom box color: </source>
        <translation>Couleur spécifique de boîte:</translation>
    </message>
    <message>
        <location filename="../../../../../../neurosvn/anatomist/anatomist-free/trunk/shared/python_plugins/selection-qt4.ui" line="231"/>
        <source>...</source>
        <translation>...</translation>
    </message>
</context>
</TS>
