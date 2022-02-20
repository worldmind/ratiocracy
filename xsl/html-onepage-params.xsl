<?xml version='1.0'?>
<xsl:stylesheet 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:import href="/usr/share/xml/docbook/stylesheet/docbook-xsl-ns/html/docbook.xsl"/>

<xsl:output method="html"
            encoding="UTF-8"
            indent="no"/>

 <xsl:param name="toc.section.depth">5</xsl:param>
 <xsl:param name="base.dir">../worldmind.github.io/download/html/</xsl:param>
 <xsl:param name="section.autolabel" select="1"></xsl:param>

</xsl:stylesheet>
