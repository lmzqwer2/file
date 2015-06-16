#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'lmzqwer2'

import os.path
import magic

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

extname = {
	'sh'	: 'bash',
	'cs'	: 'csharp',
	'cpp'	: 'cpp',
	'c'		: 'c',
	'cc'	: 'cpp',
	'h'		: 'cpp',
	'css'	: 'css',
	'js'	: 'js',
	'coffee': 'ruby',
	'json'	: 'js',
	'java'	: 'java',
	'php'	: 'php',
	'txt'	: 'plain',
	'py'	: 'python',
	'rb'	: 'ruby',
	'sql'	: 'sql',
	'vb'	: 'vb',
	'xml'	: 'xml',
	'html'	: 'xml',
	'htm'	: 'xml',
	'diff'	: 'diff',
	'patch'	: 'patch',
}

jsname = {
	'as3'			: 'shBrushAS3.js',
	'actionscript3'	: 'shBrushAS3.js',
	'bash'	: 'shBrushBash.js',
	'shell'	: 'shBrushBash.js',
	'cf'	: 'shBrushColdFusion.js',
	'coldfusion': 'shBrushColdFusion.js',
	'c-sharp'	: 'shBrushCSharp.js',
	'csharp'	: 'shBrushCSharp.js',
	'cpp'	: 'shBrushCpp.js',
	'c'		: 'shBrushCpp.js',
	'css'	: 'shBrushCss.js',
	'delphi': 'shBrushDelphi.js',
	'pas'	: 'shBrushDelphi.js',
	'pascal': 'shBrushDelphi.js',
	'diff'	: 'shBrushDiff.js',
	'patch'	: 'shBrushDiff.js',
	'erl'	: 'shBrushErlang.js',
	'erlang': 'shBrushErlang.js',
	'groovy': 'shBrushGroovy.js',
	'js'		: 'shBrushJScript.js',
	'jscript'	: 'shBrushJScript.js',
	'javascript': 'shBrushJScript.js',
	'java'	: 'shBrushJava.js',
	'jfx'	: 'shBrushJavaFX.js',
	'javafx': 'shBrushJavaFX.js',
	'perl'	: 'shBrushPerl.js',
	'pl'	: 'shBrushPerl.js',
	'php'	: 'shBrushPhp.js',
	'plain'	: 'shBrushPlain.js',
	'text'	: 'shBrushPlain.js',
	'ps'		: 'shBrushPowerShell.js',
	'powershell': 'shBrushPowerShell.js',
	'py'	: 'shBrushPython.js',
	'python': 'shBrushPython.js',
	'rails'	: 'shBrushRuby.js',
	'ror'	: 'shBrushRuby.js',
	'ruby'	: 'shBrushRuby.js',
	'scala'	: 'shBrushScala.js',
	'sql'	: 'shBrushSql.js',
	'vb'	: 'shBrushVb.js',
	'vbnet'	: 'shBrushVb.js',
	'xml'	: 'shBrushXml.js',
	'xhtml'	: 'shBrushXml.js',
	'xslt'	: 'shBrushXml.js',
	'html'	: 'shBrushXml.js',
	'xhtml'	: 'shBrushXml.js',
}

ms = magic.open(magic.NONE)
ms.load()

def filetype(name):
	fileinfo =  ms.file(name)
	f = os.path.splitext(name)
	ext = f[-1] if len(f)>1 else 'txt'
	ext = ext.strip('.')
	langtype = extname.get(ext, 'text')
	jsfile = jsname.get(langtype) if langtype is not type else None
	return {'readable': len(fileinfo.split('text'))>1, 'ext': langtype, 'js': jsfile}

if __name__ == '__main__':
	pass
