<?xml version="1.0" encoding="utf-8"?>
<!--
   GPL v3
-->
<xsl:stylesheet version="2.0" exclude-result-prefixes="#all"
   xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
   xmlns:db="http://docbook.org/ns/docbook"
   xmlns:xlink="http://www.w3.org/1999/xlink"
   xmlns="http://www.gribuser.ru/xml/fictionbook/2.0">

   <xsl:key name="biblioentry" match="db:bibliography/db:biblioentry" use="db:abbrev"/>

   <xsl:template match="db:book">
      <FictionBook>
         <xsl:namespace name="xlink" select="'http://www.w3.org/1999/xlink'"/>
         <description>
            <title-info>
               <genre>sci_politics</genre>
               <xsl:apply-templates select="db:info/db:author" mode="#current"/>
               <xsl:apply-templates select="db:info/db:title" mode="#current"/>
               <xsl:apply-templates select="@xml:lang" mode="#current"/>
            </title-info>
            <document-info>
               <xsl:apply-templates select="db:info/db:author" mode="#current"/>
               <date>
                  <xsl:value-of select="format-date(current-date(), '[Y0001]-[M01]-[D01]')"/>
               </date>
               <xsl:apply-templates select="@xml:id" mode="#current"/>
               <version>1.0</version>
            </document-info>
            <publish-info>
               <xsl:apply-templates select="db:info/(db:pubdate, db:biblioid)" mode="#current"/>
            </publish-info>
            <!-- must exclude all elements selected above -->
            <xsl:apply-templates select="db:info/db:*[not(local-name() = ('title', 'subtitle', 'author', 'pubdate', 'biblioid'))]" mode="custom-info"/>
         </description>
         <body>
            <xsl:apply-templates select="db:chapter" mode="#current"/>
         </body>
         <body name="notes">
            <xsl:apply-templates select="db:*[not(local-name() = ('info', 'chapter'))]" mode="notes"/>
            <xsl:comment>index</xsl:comment>
            <section id="{generate-id()}">
               <title>
                  <p>Index</p>
               </title>
            </section>
            <xsl:for-each-group select=".//db:indexterm/db:primary" group-by=".">
               <section id="{generate-id()}">
                  <title>
                     <p>
                        <xsl:value-of select="current-grouping-key()"/>
                     </p>
                  </title>
                  <xsl:for-each select="current-group()/ancestor::db:*[@xml:id]">
                     <p>
                        <a xlink:href="#{@xml:id}">
                           <xsl:value-of select="@xml:id"/>
                        </a>
                     </p>
                  </xsl:for-each>
               </section>
            </xsl:for-each-group>
            <xsl:comment>/index</xsl:comment>
         </body>
      </FictionBook>
   </xsl:template>

   <xsl:template match="text()"/>

   <xsl:template match="@xml:id">
      <xsl:attribute name="id" select="."/>
   </xsl:template>

   <xsl:template match="db:book/@xml:id">
      <id>
         <xsl:value-of select="."/>
      </id>
   </xsl:template>

   <!--
      ## description
   -->

   <xsl:template match="db:book/@xml:lang">
      <lang>
         <xsl:value-of select="."/>
      </lang>
   </xsl:template>

   <xsl:template match="db:book/db:info/db:title">
      <book-title>
         <xsl:value-of select="."/>
         <xsl:variable name="subtitle" select="../db:subtitle"/>
         <xsl:if test="$subtitle">
            <xsl:text>. </xsl:text>
            <xsl:value-of select="$subtitle"/>
         </xsl:if>
      </book-title>
   </xsl:template>

   <xsl:template match="db:info/db:author">
      <author>
         <xsl:apply-templates mode="#current"/>
      </author>
   </xsl:template>

   <xsl:template match="db:personname/db:firstname">
      <first-name>
         <xsl:value-of select="."/>
      </first-name>
   </xsl:template>

   <xsl:template match="db:personname/db:surname">
      <last-name>
         <xsl:value-of select="."/>
      </last-name>
   </xsl:template>

   <xsl:template match="db:personname/db:othername[@role = 'middle']">
      <middle-name>
         <xsl:value-of select="."/>
      </middle-name>
   </xsl:template>

   <xsl:template match="db:author/db:email">
      <email>
         <xsl:value-of select="."/>
      </email>
   </xsl:template>

   <xsl:template match="db:author/db:uri[@type = 'website']">
      <home-page>
         <xsl:value-of select="."/>
      </home-page>
   </xsl:template>

   <xsl:template match="db:info/db:pubdate">
      <year>
         <xsl:value-of select="."/>
      </year>
   </xsl:template>

   <xsl:template match="db:info/db:biblioid">
      <isbn>
         <xsl:value-of select="."/>
      </isbn>
   </xsl:template>

   <xsl:template match="db:*" mode="custom-info">
      <custom-info info-type="{local-name()}">
         <xsl:value-of select="normalize-space()"/>
      </custom-info>
   </xsl:template>

   <!--
      ## body
   -->

   <xsl:template match="db:chapter | db:sect1 | db:sect2 | db:sect3 | db:sect4 | db:sect5">
      <section>
         <xsl:apply-templates select="@xml:id" mode="#current"/>
         <xsl:apply-templates mode="#current"/>
      </section>
   </xsl:template>

   <xsl:template match="db:title | db:glossentry/db:glossterm">
      <title>
         <p>
            <xsl:value-of select="."/>
         </p>
      </title>
   </xsl:template>

   <xsl:template match="db:epigraph">
      <epigraph>
         <xsl:apply-templates select="db:* except db:attribution" mode="#current"/>
         <xsl:apply-templates select="db:attribution" mode="#current"/>
      </epigraph>
   </xsl:template>

   <xsl:template match="db:attribution">
      <text-author>
         <xsl:apply-templates mode="#current"/>
      </text-author>
   </xsl:template>

   <xsl:template match="db:attribution//text()">
      <xsl:copy/>
   </xsl:template>

   <xsl:template match="db:para">
      <p>
         <xsl:apply-templates mode="#current"/>
      </p>
   </xsl:template>

   <xsl:template match="db:para[db:orderedlist or db:itemizedlist]">
      <xsl:for-each-group select="node()[self::* or self::text()[normalize-space()]]" group-starting-with="db:orderedlist | db:itemizedlist">
         <xsl:choose>
            <xsl:when test="self::db:orderedlist or self::db:itemizedlist">
               <xsl:apply-templates select="current-group()[1]" mode="#current"/>
               <xsl:if test="current-group()[2]">
                  <p>
                     <xsl:apply-templates select="current-group()[position() gt 1]" mode="#current"/>
                  </p>
               </xsl:if>
            </xsl:when>
            <xsl:otherwise>
               <p>
                  <xsl:apply-templates select="current-group()" mode="#current"/>
               </p>
            </xsl:otherwise>
         </xsl:choose>
      </xsl:for-each-group>
   </xsl:template>

   <xsl:template match="db:para//text()">
      <xsl:copy/>
   </xsl:template>

   <xsl:template match="db:link">
      <a>
         <xsl:copy-of select="@xlink:*"/>
         <xsl:choose>
            <xsl:when test="* or text()">
               <xsl:apply-templates mode="#current"/>
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="@xlink:href"/>
            </xsl:otherwise>
         </xsl:choose>
      </a>
   </xsl:template>

   <xsl:template match="db:glossterm">
      <a xlink:href="#{@linkend}" type="note">
         <xsl:apply-templates mode="#current"/>
      </a>
   </xsl:template>

   <xsl:template match="db:xref">
      <a xlink:href="#{@linkend}">
         <xsl:value-of select="@linkend"/>
      </a>
   </xsl:template>

   <xsl:template match="db:citation">
      <a xlink:href="#{generate-id(key('biblioentry', .))}" type="note">
         <xsl:apply-templates mode="#current"/>
      </a>
   </xsl:template>

   <xsl:template match="db:subscript">
      <sub>
         <xsl:apply-templates mode="#current"/>
      </sub>
   </xsl:template>

   <xsl:template match="db:superscript">
      <sup>
         <xsl:apply-templates mode="#current"/>
      </sup>
   </xsl:template>

   <xsl:template match="db:code">
      <code>
         <xsl:apply-templates mode="#current"/>
      </code>
   </xsl:template>

   <xsl:template match="db:emphasis">
      <emphasis>
         <xsl:apply-templates mode="#current"/>
      </emphasis>
   </xsl:template>

   <xsl:template match="db:emphasis[@role = 'strikethrough']">
      <strikethrough>
         <xsl:apply-templates mode="#current"/>
      </strikethrough>
   </xsl:template>

   <xsl:template match="db:emphasis[@role = 'strong']">
      <strong>
         <xsl:apply-templates mode="#current"/>
      </strong>
   </xsl:template>

   <xsl:template match="db:imagedata[@fileref]">
      <image xlink:href="{@fileref}"/>
   </xsl:template>

   <xsl:template match="db:quote">
      <xsl:text>«</xsl:text>
      <xsl:value-of select="."/>
      <xsl:text>»</xsl:text>
   </xsl:template>

   <xsl:template match="db:blockquote">
      <cite>
         <xsl:apply-templates mode="#current"/>
      </cite>
   </xsl:template>

   <xsl:template match="db:footnote">
      <emphasis>
         <xsl:apply-templates mode="#current"/>
      </emphasis>
   </xsl:template>

   <xsl:template match="db:orderedlist/db:listitem/db:*[1]">
      <p>
         <xsl:value-of select="count(../preceding-sibling::db:listitem) + 1"/>
         <xsl:text>. </xsl:text>
         <xsl:apply-templates mode="#current"/>
      </p>
   </xsl:template>

   <xsl:template match="db:itemizedlist/db:listitem/db:*[1]">
      <p>
         <xsl:text>• </xsl:text>
         <xsl:apply-templates mode="#current"/>
      </p>
   </xsl:template>

   <!--
      ## notes
   -->

   <!--<xsl:template match="db:*[node()]" mode="notes">
      <section id="{(@xml:id, generate-id())[1]}">
         <xsl:comment select="local-name()"/>
         <xsl:apply-templates mode="#default"/>
      </section>
   </xsl:template>-->

   <xsl:template match="db:*[node()]" mode="notes">
      <xsl:comment select="local-name()"/>
      <section id="{(@xml:id, generate-id())[1]}">
         <xsl:apply-templates select="db:title" mode="#default"/>
      </section>
      <xsl:apply-templates select="db:* except db:title" mode="#default"/>
      <xsl:comment select="concat('/', local-name())"/>
   </xsl:template>

   <xsl:template match="db:glossentry">
      <section>
         <xsl:apply-templates select="@xml:id" mode="#current"/>
         <xsl:apply-templates mode="#current"/>
      </section>
   </xsl:template>

   <xsl:template match="db:biblioentry">
      <section id="{generate-id()}">
         <xsl:apply-templates select="db:title" mode="#current"/>
         <xsl:apply-templates select="db:* except db:title" mode="#current"/>
      </section>
   </xsl:template>

   <xsl:template match="db:biblioentry/db:*[not(self::db:title)]">
      <p>
         <xsl:value-of select="local-name()"/>
         <xsl:text>: </xsl:text>
         <xsl:value-of select="."/>
      </p>
   </xsl:template>

   <xsl:template match="db:biblioentry/db:bibliosource[@class = 'uri']" priority="10">
      <p>
         <xsl:value-of select="local-name()"/>
         <xsl:text>: </xsl:text>
         <xsl:apply-templates select="db:link" mode="#current"/>
      </p>
   </xsl:template>

</xsl:stylesheet>
