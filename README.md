# Cmder for Sublime Text

Cmder for Sublime Text run customer command, `Cmder for Sublime Text`  run any command. You can use it to run any os command, such as python, java, ruby, go, c, c++, github, docker, heroku, etc.

# How tu run

shortkey: `ctrl+alt+i`

# How to config

## custom config

```json
{
	// ${workspaceFolder} - the path of the folder opened in Sublime
	// ${workspaceFolderBasename} - the name of the folder opened in Sublime without any slashes (/)
	// ${file} - the current opened file
	// ${relativeFile} - the current opened file relative to workspaceFolder
	// ${fileBasename} - the current opened file's basename
	// ${fileBasenameNoExtension} - the current opened file's basename with no file extension
	// ${fileDirname} - the current opened file's dirname
	// ${fileExtname} - the current opened file's extension
	// ${cwd} - the task runner's current working directory on startup
	// ${selectedText} - the current selected text in the active file
    // ${input:custom_string} - Custom String
    // set default input value in "custom_env" object
	"tasks" : [
		{
			"label" : "echo:env",
			"command": "echo JAVA_HOME:${env:JAVA_HOME}, USERPROFILE:${env:USERPROFILE}"
		},
		{
			"label" : "java:version",
			"command": "java -version"
		},
		{
			"label" : "windows:new:file",
			"command": "type nul > \"${input:workspaceFolder}/${input:file_name}\""
		},
		{
			"label" : "linux:new:file",
			"command": "touch \"${input:workspaceFolder}/${input:file_name}\""
		},
		{
			"label" : "python:run",
			"command": "python ${file}"
		},
		{
			"label" : "python:run",
			"os_termial": true,
			"command": "python ${file}"
		},
		{
			"label" : "node:run",
			"command": "node ${file}"
		},
		{
			"label" : "echo:test",
			"command": "echo ${input:param1}, ${input:log_file}, ${select:LOGLEVEL}"
		}
	],
    "custom_env" : {
        "log_file" : "./sfdc_tail.log",
        "LOGLEVEL" : ["trace", "debug", "info", "warn", "error", "fatal"]
    }
}
```

## Predefined variables

* ${workspaceFolder} - the path of the folder opened in Sublime
* ${workspaceFolderBasename} - the name of the folder opened in Sublime without any slashes (/)
* ${file} - the current opened file
* ${relativeFile} - the current opened file relative to workspaceFolder
* ${fileBasename} - the current opened file's basename
* ${fileBasenameNoExtension} - the current opened file's basename with no file extension
* ${fileDirname} - the current opened file's dirname
* ${fileExtname} - the current opened file's extension
* ${cwd} - the task runner's current working directory on startup
* ${selectedText} - the current selected text in the active file

## Customer variables

## input variables: 

* `${input:variable_name}` - Custom Input String

## select variables: 

* `${select:variable_name}` - Custom Input String

example:
```json
{
	"tasks" : [
		{
			"label" : "echo:test",
			"command": "echo ${input:param1}, ${input:param2}, ${select:param3}"
		}
	],
    "custom_env" : {
        "param2" : "./default_value",
        "param3" : ["trace", "debug", "info", "warn", "error", "fatal"]
    }
}
```
we defined 3 variable.

* `param1` is empty string.
* `param2` is an input string
* `param3` is a select list

## support System env

`${env:NAME_OF_SYS_ENV}`

such as `${env:USERPROFILE}`,  `${env:JAVA_HOME}`

example:
```json
{
	"tasks" : [
		{
			"label" : "echo:test",
			"command": "echo ${env:USERPROFILE}"
		}
	],
    "custom_env" : {
    }
}
```

## other command params.

* `encoding`: you can custom the `encoding`
* `os_termial`: run the command in os termail

```js
		{
			"label" : "node",
			"encoding" : "UTF-8",
			"command": "node -v"
		},
```

# More example

## new File

```js
	"tasks" : [
		{
			"label" : "windows:new:file",
			"command": "type nul > \"${input:workspaceFolder}/${input:file_name}\""
		},
		{
			"label" : "linux:new:file",
			"command": "touch \"${input:workspaceFolder}/${input:file_name}\""
		},
	],
    "custom_env" : {
    }
}
```


# about author
[Exia.huang](https://github.com/exiahuang)

[Github](https://github.com/exiahuang/Cmder)

[Cmder Wiki](https://github.com/exiahuang/Cmder/wiki)

[Cmder Issues](https://github.com/exiahuang/Cmder/issues)