[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern("^\d+$")]
    [string]$SpaceId,

    [string]$BaseName = "个人知识生长系统｜工作台",

    [string]$Profile = "cli_aa1ff2a548b85bd3",

    [string]$BaseToken,

    [string]$ConfigPath,

    [switch]$Apply
)

$ErrorActionPreference = "Stop"
$minimumVersion = [version]"1.0.92"
$userProfilePath = [Environment]::GetFolderPath("UserProfile")

if ([string]::IsNullOrWhiteSpace($ConfigPath)) {
    $ConfigPath = if ([string]::IsNullOrWhiteSpace($env:FEISHU_KG_CONFIG)) {
        Join-Path $userProfilePath ".knowledge-growth\config.json"
    } else {
        $env:FEISHU_KG_CONFIG
    }
}

$tableNames = @("来源收件箱", "知识节点", "知识补丁", "目标", "成长缺口", "行动与验证")
$topWikiNodes = @(
    "00｜知识生长首页",
    "10｜当前阶段",
    "20｜世界模型",
    "30｜能力模型",
    "40｜自我模型",
    "50｜实践模型",
    "90｜系统说明"
)

function New-SelectField {
    param(
        [string]$Name,
        [string[]]$Options,
        [bool]$Multiple = $false
    )

    return [ordered]@{
        name = $Name
        type = "select"
        multiple = $Multiple
        options = @($Options | ForEach-Object { [ordered]@{ name = $_ } })
    }
}

function New-RatingField {
    param([string]$Name)
    return [ordered]@{
        name = $Name
        type = "number"
        style = [ordered]@{ type = "rating"; icon = "star"; min = 1; max = 5 }
    }
}

function New-DateField {
    param([string]$Name)
    return [ordered]@{
        name = $Name
        type = "datetime"
        style = [ordered]@{ format = "yyyy-MM-dd HH:mm" }
    }
}

$schemas = [ordered]@{}
$schemas["来源收件箱"] = @(
    [ordered]@{ name = "标题"; type = "text" },
    (New-SelectField "来源类型" @("微信公众号", "小红书", "抖音", "B站", "YouTube", "X", "微信群", "QQ群", "网页", "书籍", "纪录片", "生活事件", "JD", "面经", "项目材料", "其他") $true),
    [ordered]@{ name = "原始链接"; type = "text"; style = [ordered]@{ type = "url" } },
    [ordered]@{ name = "原文或转述"; type = "text" },
    [ordered]@{ name = "我的触发点"; type = "text" },
    (New-SelectField "处理意图" @("待读", "分析融合", "能力对标", "生活复盘", "暂存")),
    (New-SelectField "状态" @("待处理", "处理中", "待确认", "已融合", "仅归档", "失效")),
    [ordered]@{ name = "当前目标"; type = "text" },
    [ordered]@{ name = "内容指纹"; type = "text" },
    (New-RatingField "信息质量"),
    [ordered]@{ name = "创建时间"; type = "created_at"; style = [ordered]@{ format = "yyyy-MM-dd HH:mm" } },
    [ordered]@{ name = "更新时间"; type = "updated_at"; style = [ordered]@{ format = "yyyy-MM-dd HH:mm" } }
)

$schemas["知识节点"] = @(
    [ordered]@{ name = "节点标题"; type = "text" },
    (New-SelectField "模型层" @("世界模型", "能力模型", "自我模型", "实践模型")),
    (New-SelectField "节点类型" @("概念", "原理", "机制", "方法", "案例", "决策规则", "能力标准", "自我模式", "项目结论")),
    (New-SelectField "状态" @("幼苗", "生长中", "稳定", "争议", "待重构", "已废弃")),
    [ordered]@{ name = "当前结论"; type = "text" },
    [ordered]@{ name = "适用边界"; type = "text" },
    [ordered]@{ name = "反例或冲突"; type = "text" },
    [ordered]@{ name = "证据摘要"; type = "text" },
    [ordered]@{ name = "Wiki链接"; type = "text"; style = [ordered]@{ type = "url" } },
    [ordered]@{ name = "稳定ID"; type = "text" },
    (New-RatingField "置信度"),
    (New-DateField "最后验证日期"),
    [ordered]@{ name = "更新时间"; type = "updated_at"; style = [ordered]@{ format = "yyyy-MM-dd HH:mm" } }
)

$schemas["知识补丁"] = @(
    [ordered]@{ name = "补丁标题"; type = "text" },
    [ordered]@{ name = "Patch ID"; type = "auto_number" },
    (New-SelectField "操作类型" @("新增", "补充", "修正", "合并", "拆分", "废弃", "无变更")),
    (New-SelectField "分析路线" @("学习", "能力", "成长")),
    (New-SelectField "状态" @("草稿", "待确认", "已批准", "已应用", "已拒绝", "待补证据")),
    [ordered]@{ name = "原结论或上下文"; type = "text" },
    [ordered]@{ name = "新增量"; type = "text" },
    [ordered]@{ name = "冲突与边界"; type = "text" },
    [ordered]@{ name = "合并后文本"; type = "text" },
    (New-SelectField "证据强度" @("弱", "中", "强")),
    (New-RatingField "AI置信度"),
    [ordered]@{ name = "用户关键输出"; type = "text" },
    [ordered]@{ name = "反向问题"; type = "text" },
    [ordered]@{ name = "创建时间"; type = "created_at"; style = [ordered]@{ format = "yyyy-MM-dd HH:mm" } },
    (New-DateField "确认时间"),
    (New-DateField "应用时间")
)

$schemas["目标"] = @(
    [ordered]@{ name = "目标名称"; type = "text" },
    (New-SelectField "领域" @("求职", "项目", "技术", "产品", "表达", "健康", "财务", "生活", "阅读", "其他")),
    (New-SelectField "层级" @("阶段目标", "项目目标", "能力目标", "习惯目标")),
    (New-SelectField "状态" @("进行中", "待开始", "暂停", "完成", "放弃")),
    [ordered]@{ name = "成功标准"; type = "text" },
    (New-DateField "截止日期"),
    (New-RatingField "当前优先级"),
    (New-RatingField "边际价值"),
    [ordered]@{ name = "下一里程碑"; type = "text" },
    [ordered]@{ name = "复盘节奏"; type = "text" },
    [ordered]@{ name = "更新时间"; type = "updated_at"; style = [ordered]@{ format = "yyyy-MM-dd HH:mm" } }
)

$levelOptions = @("未知", "入门", "可复述", "可操作", "可迁移", "可教学")
$schemas["成长缺口"] = @(
    [ordered]@{ name = "缺口名称"; type = "text" },
    (New-SelectField "缺口类型" @("知识", "技能", "证据", "表达", "行为", "决策", "系统")),
    (New-SelectField "当前水平" $levelOptions),
    (New-SelectField "目标水平" $levelOptions),
    (New-RatingField "紧迫度"),
    (New-RatingField "影响度"),
    [ordered]@{ name = "当前证据"; type = "text" },
    [ordered]@{ name = "根因假设"; type = "text" },
    [ordered]@{ name = "最小补齐路径"; type = "text" },
    (New-SelectField "状态" @("待验证", "待学习", "学习中", "待实战", "已补齐", "暂缓")),
    (New-DateField "下次复查"),
    [ordered]@{ name = "更新时间"; type = "updated_at"; style = [ordered]@{ format = "yyyy-MM-dd HH:mm" } }
)

$schemas["行动与验证"] = @(
    [ordered]@{ name = "行动名称"; type = "text" },
    (New-SelectField "类型" @("学习任务", "刻意练习", "项目实验", "行为实验", "决策协议", "输出作品", "面试验证")),
    [ordered]@{ name = "假设"; type = "text" },
    [ordered]@{ name = "最小动作"; type = "text" },
    [ordered]@{ name = "完成标准"; type = "text" },
    (New-DateField "截止时间"),
    (New-SelectField "状态" @("待做", "进行中", "完成", "失败", "取消")),
    [ordered]@{ name = "结果"; type = "text" },
    [ordered]@{ name = "证据"; type = "text" },
    [ordered]@{ name = "复盘"; type = "text" },
    [ordered]@{ name = "下一步"; type = "text" },
    [ordered]@{ name = "成本分钟"; type = "number"; style = [ordered]@{ type = "plain"; precision = 0 } },
    (New-RatingField "价值评分"),
    [ordered]@{ name = "创建时间"; type = "created_at"; style = [ordered]@{ format = "yyyy-MM-dd HH:mm" } },
    [ordered]@{ name = "更新时间"; type = "updated_at"; style = [ordered]@{ format = "yyyy-MM-dd HH:mm" } }
)

$relations = @(
    [ordered]@{ key = "来源-知识"; table = "来源收件箱"; field = [ordered]@{ name = "关联知识节点"; type = "link"; link_table = "知识节点"; bidirectional = $true; bidirectional_link_field_name = "来源" } },
    [ordered]@{ key = "补丁-知识"; table = "知识补丁"; field = [ordered]@{ name = "目标知识节点"; type = "link"; link_table = "知识节点"; bidirectional = $true; bidirectional_link_field_name = "补丁历史" } },
    [ordered]@{ key = "补丁-来源"; table = "知识补丁"; field = [ordered]@{ name = "依据来源"; type = "link"; link_table = "来源收件箱"; bidirectional = $true; bidirectional_link_field_name = "产生补丁" } },
    [ordered]@{ key = "缺口-目标"; table = "成长缺口"; field = [ordered]@{ name = "对应目标"; type = "link"; link_table = "目标"; bidirectional = $true; bidirectional_link_field_name = "关联缺口" } },
    [ordered]@{ key = "行动-目标"; table = "行动与验证"; field = [ordered]@{ name = "对应目标"; type = "link"; link_table = "目标"; bidirectional = $true; bidirectional_link_field_name = "关联行动" } },
    [ordered]@{ key = "行动-缺口"; table = "行动与验证"; field = [ordered]@{ name = "对应缺口"; type = "link"; link_table = "成长缺口"; bidirectional = $true; bidirectional_link_field_name = "验证行动" } },
    [ordered]@{ key = "行动-知识"; table = "行动与验证"; field = [ordered]@{ name = "关联知识节点"; type = "link"; link_table = "知识节点"; bidirectional = $true; bidirectional_link_field_name = "关联行动" } }
)

function Convert-LarkJson {
    param([object[]]$OutputLines)

    $text = ($OutputLines | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine
    $firstBrace = $text.IndexOf("{")
    $lastBrace = $text.LastIndexOf("}")
    if ($firstBrace -lt 0 -or $lastBrace -le $firstBrace) {
        throw "lark-cli 未返回可解析的 JSON：`n$text"
    }

    $jsonText = $text.Substring($firstBrace, $lastBrace - $firstBrace + 1)
    try {
        return $jsonText | ConvertFrom-Json
    } catch {
        throw "无法解析 lark-cli JSON：`n$jsonText"
    }
}

function Invoke-LarkNative {
    param([string[]]$Arguments)

    # Windows PowerShell 5.1 wraps native stderr lines as ErrorRecord objects.
    # lark-cli is launched through a Node PowerShell shim and may legitimately
    # write progress or JSON diagnostics to stderr. With the script-wide
    # ErrorActionPreference=Stop, the first stderr line would terminate the
    # script before we could inspect the exit code and JSON envelope. Node emits
    # UTF-8, while Windows PowerShell may decode captured native output with the
    # legacy console code page, corrupting Chinese text and the JSON quotes.
    $previousPreference = $ErrorActionPreference
    $previousConsoleOutputEncoding = [Console]::OutputEncoding
    $previousOutputEncoding = $OutputEncoding
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    try {
        $ErrorActionPreference = "Continue"
        [Console]::OutputEncoding = $utf8NoBom
        $OutputEncoding = $utf8NoBom
        $output = @(& lark-cli @Arguments 2>&1)
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
        [Console]::OutputEncoding = $previousConsoleOutputEncoding
        $OutputEncoding = $previousOutputEncoding
    }

    return [pscustomobject]@{
        Output = $output
        ExitCode = $exitCode
    }
}

function Invoke-LarkJson {
    param([string[]]$Arguments)

    $allArguments = @($Arguments + @("--as", "user", "--format", "json"))
    $displayArguments = @($allArguments | ForEach-Object {
        if ($_.Length -gt 120) { "<json:$($_.Length) chars>" } else { $_ }
    })
    Write-Host ("lark-cli " + ($displayArguments -join " ")) -ForegroundColor DarkGray
    $invocation = Invoke-LarkNative -Arguments $allArguments
    $response = Convert-LarkJson -OutputLines $invocation.Output

    if ($invocation.ExitCode -ne 0 -or -not $response.ok) {
        $message = if ($response.error.message) { $response.error.message } else { "未知错误" }
        $hint = if ($response.error.hint) { " 提示：$($response.error.hint)" } else { "" }
        throw "lark-cli 失败：$message$hint"
    }
    return $response
}

function Invoke-LarkJsonPayload {
    param(
        [string[]]$Arguments,
        [string]$JsonFlag,
        [string]$Json
    )

    # Passing long JSON directly through Windows PowerShell -> lark-cli.ps1 ->
    # Node can strip or reinterpret the embedded quotes. lark-cli supports
    # @file.json for complex JSON/DSL, but only accepts a relative path inside
    # the current directory (absolute/temp paths are rejected), so write UTF-8
    # without BOM into the working directory and always remove the temporary
    # payload after the command finishes.
    $fileName = "feishu-kg-{0}.json" -f ([guid]::NewGuid().ToString("N"))
    $tempPath = Join-Path -Path (Get-Location).ProviderPath -ChildPath $fileName
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    try {
        [IO.File]::WriteAllText($tempPath, $Json, $utf8NoBom)
        return Invoke-LarkJson -Arguments @($Arguments + @($JsonFlag, "@./$fileName"))
    } finally {
        if (Test-Path -LiteralPath $tempPath) {
            Remove-Item -LiteralPath $tempPath -Force -ErrorAction SilentlyContinue
        }
    }
}

function Find-FirstValue {
    param(
        [object]$Object,
        [string[]]$Names
    )

    if ($null -eq $Object) { return $null }
    if ($Object -is [string] -or $Object -is [ValueType]) { return $null }

    if ($Object -is [System.Collections.IEnumerable] -and -not ($Object -is [pscustomobject])) {
        foreach ($item in $Object) {
            $found = Find-FirstValue -Object $item -Names $Names
            if ($null -ne $found) { return $found }
        }
        return $null
    }

    foreach ($property in $Object.PSObject.Properties) {
        if ($Names -contains $property.Name -and $null -ne $property.Value -and "$($property.Value)" -ne "") {
            return $property.Value
        }
    }
    foreach ($property in $Object.PSObject.Properties) {
        $found = Find-FirstValue -Object $property.Value -Names $Names
        if ($null -ne $found) { return $found }
    }
    return $null
}

function Find-NamedId {
    param(
        [object]$Object,
        [string]$ExpectedName,
        [string[]]$IdNames
    )

    if ($null -eq $Object) { return $null }
    if ($Object -is [string] -or $Object -is [ValueType]) { return $null }

    if ($Object -is [System.Collections.IEnumerable] -and -not ($Object -is [pscustomobject])) {
        foreach ($item in $Object) {
            $found = Find-NamedId -Object $item -ExpectedName $ExpectedName -IdNames $IdNames
            if ($null -ne $found) { return $found }
        }
        return $null
    }

    $nameValue = $null
    foreach ($candidate in @("name", "title")) {
        $property = $Object.PSObject.Properties[$candidate]
        if ($property) { $nameValue = "$($property.Value)"; break }
    }
    if ($nameValue -eq $ExpectedName) {
        foreach ($idName in $IdNames) {
            $idProperty = $Object.PSObject.Properties[$idName]
            if ($idProperty -and "$($idProperty.Value)" -ne "") {
                return "$($idProperty.Value)"
            }
        }
    }

    foreach ($property in $Object.PSObject.Properties) {
        $found = Find-NamedId -Object $property.Value -ExpectedName $ExpectedName -IdNames $IdNames
        if ($null -ne $found) { return $found }
    }
    return $null
}

function Save-Config {
    param([System.Collections.IDictionary]$Config)

    $Config.updated_at = (Get-Date).ToString("o")
    $directory = Split-Path -Parent $ConfigPath
    if (-not [string]::IsNullOrWhiteSpace($directory) -and -not (Test-Path $directory)) {
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }
    $Config | ConvertTo-Json -Depth 20 | Set-Content -Path $ConfigPath -Encoding UTF8
}

function New-Config {
    $config = [ordered]@{
        schema_version = "1.0"
        identity = "user"
        profile = $Profile
        space_id = $SpaceId
        base_token = ""
        tables = [ordered]@{}
        relations_created = @()
        wiki_nodes = [ordered]@{}
        created_at = (Get-Date).ToString("o")
        updated_at = (Get-Date).ToString("o")
    }
    foreach ($name in $tableNames) { $config.tables[$name] = "" }
    return $config
}

function Import-ExistingConfig {
    $config = New-Config
    if (-not (Test-Path $ConfigPath)) { return $config }

    $old = Get-Content -Path $ConfigPath -Raw | ConvertFrom-Json
    if ($old.space_id -and "$($old.space_id)" -ne $SpaceId) {
        throw "现有配置的 space_id 为 $($old.space_id)，与参数 $SpaceId 不一致。"
    }
    if ($old.base_token) { $config.base_token = "$($old.base_token)" }
    if ($old.created_at) { $config.created_at = "$($old.created_at)" }
    if ($old.tables) {
        foreach ($name in $tableNames) {
            $property = $old.tables.PSObject.Properties[$name]
            if ($property) { $config.tables[$name] = "$($property.Value)" }
        }
    }
    if ($old.relations_created) { $config.relations_created = @($old.relations_created) }
    if ($old.wiki_nodes) {
        foreach ($property in $old.wiki_nodes.PSObject.Properties) {
            $config.wiki_nodes[$property.Name] = $property.Value
        }
    }
    return $config
}

if (-not (Get-Command lark-cli -ErrorAction SilentlyContinue)) {
    throw "未找到 lark-cli。请先安装并确认 lark-cli --version 可用。"
}

$hermesHome = [Environment]::GetEnvironmentVariable("HERMES_HOME", "Process")
if (-not [string]::IsNullOrWhiteSpace($hermesHome)) {
    throw @"
检测到当前 PowerShell 继承了 HERMES_HOME，lark-cli 会因此进入 Hermes 上下文，而不会使用你已经登录成功的本地 profile。
本 Skill 不依赖 Hermes，请不要执行 lark-cli config bind。先在当前终端运行：
  Remove-Item Env:HERMES_HOME -ErrorAction SilentlyContinue
  lark-cli whoami
确认 identity=user 且 tokenStatus=ready 后，再重新运行 bootstrap.ps1。
这只清除当前进程变量，不会删除 Hermes 或飞书登录配置。若新终端仍复现，请按 INSTALL.md 的“Hermes 上下文误判”检查用户级环境变量。
"@
}

$versionInvocation = Invoke-LarkNative -Arguments @("--version")
$versionText = ($versionInvocation.Output | Out-String).Trim()
if ($versionInvocation.ExitCode -ne 0) {
    throw "lark-cli --version 执行失败：$versionText"
}
$versionMatch = [regex]::Match($versionText, "(\d+\.\d+\.\d+)")
if (-not $versionMatch.Success) {
    throw "无法识别 lark-cli 版本：$versionText"
}
$actualVersion = [version]$versionMatch.Groups[1].Value
if ($actualVersion -lt $minimumVersion) {
    throw "需要 lark-cli >= $minimumVersion，当前为 $actualVersion。"
}

$whoamiInvocation = Invoke-LarkNative -Arguments @("whoami")
$whoami = Convert-LarkJson -OutputLines $whoamiInvocation.Output
if ($whoamiInvocation.ExitCode -ne 0) {
    $message = if ($whoami.error.message) { $whoami.error.message } else { "未知错误" }
    $hint = if ($whoami.error.hint) { " 提示：$($whoami.error.hint)" } else { "" }
    throw "lark-cli whoami 执行失败：$message$hint"
}
if ($whoami.tokenStatus -eq "needs_refresh") {
    throw "lark-cli user token 需要重新授权。请使用与原登录相同的 domain/scope 运行 auth login，确认 whoami 的 tokenStatus=ready 后重试。"
}
if ($whoami.tokenStatus -ne "ready" -or $whoami.identity -ne "user") {
    throw "lark-cli 当前不是可用的 user 身份（identity=$($whoami.identity), tokenStatus=$($whoami.tokenStatus)）。请先完成 auth login。"
}
if (-not [string]::IsNullOrWhiteSpace($Profile) -and $whoami.profile -ne $Profile) {
    throw "当前 profile 为 $($whoami.profile)，预期为 $Profile。请确认账号后重试，或显式传入正确的 -Profile。"
}

Write-Host "lark-cli $actualVersion；当前用户：$($whoami.onBehalfOf.userName)；身份：user"
Write-Host "Wiki Space：$SpaceId"
Write-Host "Base：$BaseName"
Write-Host ("数据表：" + ($tableNames -join "、"))
Write-Host ("Wiki 节点：" + ($topWikiNodes -join "、") + "；以及 2027秋招与当前行动主线")
Write-Host "配置文件：$ConfigPath"

if (-not $Apply) {
    Write-Host ""
    Write-Host "当前是预演模式，没有写入飞书或本地配置。确认后重新运行并添加 -Apply。" -ForegroundColor Yellow
    return
}

$config = Import-ExistingConfig
if (-not [string]::IsNullOrWhiteSpace($BaseToken)) {
    if ($config.base_token -and $config.base_token -ne $BaseToken) {
        throw "配置中已有不同的 base_token。请检查 $ConfigPath。"
    }
    $config.base_token = $BaseToken
    Save-Config -Config $config
}

if ([string]::IsNullOrWhiteSpace($config.base_token)) {
    $firstTable = "来源收件箱"
    $fieldJson = $schemas[$firstTable] | ConvertTo-Json -Depth 20 -Compress
    $response = Invoke-LarkJsonPayload -Arguments @("base", "+base-create", "--name", $BaseName, "--table-name", $firstTable) -JsonFlag "--fields" -Json $fieldJson
    $config.base_token = "$(Find-FirstValue -Object $response.data -Names @("base_token", "app_token"))"
    if ([string]::IsNullOrWhiteSpace($config.base_token)) {
        throw "Base 已创建，但响应中未找到 base_token。请保留 CLI 输出并人工检查。"
    }
    $firstTableId = Find-NamedId -Object $response.data -ExpectedName $firstTable -IdNames @("table_id", "id")
    if ($firstTableId) { $config.tables[$firstTable] = $firstTableId }
    Save-Config -Config $config
}

$tableList = Invoke-LarkJson @("base", "+table-list", "--base-token", $config.base_token)
foreach ($name in $tableNames) {
    if ([string]::IsNullOrWhiteSpace($config.tables[$name])) {
        $existingId = Find-NamedId -Object $tableList.data -ExpectedName $name -IdNames @("table_id", "id")
        if ($existingId) { $config.tables[$name] = $existingId }
    }
}
Save-Config -Config $config

foreach ($name in $tableNames | Select-Object -Skip 1) {
    if (-not [string]::IsNullOrWhiteSpace($config.tables[$name])) { continue }
    $fieldJson = $schemas[$name] | ConvertTo-Json -Depth 20 -Compress
    $response = Invoke-LarkJsonPayload -Arguments @("base", "+table-create", "--base-token", $config.base_token, "--name", $name) -JsonFlag "--fields" -Json $fieldJson
    $tableId = Find-NamedId -Object $response.data -ExpectedName $name -IdNames @("table_id", "id")
    if (-not $tableId) { $tableId = Find-FirstValue -Object $response.data -Names @("table_id") }
    if (-not $tableId) { throw "表 $name 已创建，但响应中未找到 table_id。" }
    $config.tables[$name] = "$tableId"
    Save-Config -Config $config
}

foreach ($relation in $relations) {
    if ($config.relations_created -contains $relation.key) { continue }
    $fieldList = Invoke-LarkJson @("base", "+field-list", "--base-token", $config.base_token, "--table-id", $config.tables[$relation.table])
    $existingFieldId = Find-NamedId -Object $fieldList.data -ExpectedName $relation.field.name -IdNames @("field_id", "id")
    if ($existingFieldId) {
        $config.relations_created = @($config.relations_created + $relation.key)
        Save-Config -Config $config
        continue
    }
    $relationJson = $relation.field | ConvertTo-Json -Depth 10 -Compress
    $null = Invoke-LarkJsonPayload -Arguments @("base", "+field-create", "--base-token", $config.base_token, "--table-id", $config.tables[$relation.table]) -JsonFlag "--json" -Json $relationJson
    $config.relations_created = @($config.relations_created + $relation.key)
    Save-Config -Config $config
}

$rootNodes = Invoke-LarkJson @("wiki", "+node-list", "--space-id", $SpaceId, "--page-all")
foreach ($title in $topWikiNodes) {
    if ($config.wiki_nodes.Contains($title)) { continue }
    $existingToken = Find-NamedId -Object $rootNodes.data -ExpectedName $title -IdNames @("node_token")
    if ($existingToken) {
        $nodeInfo = Invoke-LarkJson @("wiki", "+node-get", "--node-token", $existingToken)
        $config.wiki_nodes[$title] = [ordered]@{
            node_token = "$existingToken"
            obj_token = "$(Find-FirstValue -Object $nodeInfo.data -Names @("obj_token"))"
            obj_type = "$(Find-FirstValue -Object $nodeInfo.data -Names @("obj_type"))"
        }
        Save-Config -Config $config
        continue
    }

    $response = Invoke-LarkJson @("wiki", "+node-create", "--space-id", $SpaceId, "--title", $title)
    $nodeToken = Find-FirstValue -Object $response.data -Names @("node_token")
    $objToken = Find-FirstValue -Object $response.data -Names @("obj_token")
    $objType = Find-FirstValue -Object $response.data -Names @("obj_type")
    if (-not $nodeToken) { throw "Wiki 节点 $title 已创建，但响应中未找到 node_token。" }
    $config.wiki_nodes[$title] = [ordered]@{ node_token = "$nodeToken"; obj_token = "$objToken"; obj_type = "$objType" }
    Save-Config -Config $config
}

$stageTitle = "10｜当前阶段"
$childTitle = "2027秋招与当前行动主线"
if (-not $config.wiki_nodes.Contains($childTitle)) {
    $parentToken = "$($config.wiki_nodes[$stageTitle].node_token)"
    if ([string]::IsNullOrWhiteSpace($parentToken)) { throw "无法取得当前阶段节点 token。" }
    $children = Invoke-LarkJson @("wiki", "+node-list", "--space-id", $SpaceId, "--parent-node-token", $parentToken, "--page-all")
    $existingToken = Find-NamedId -Object $children.data -ExpectedName $childTitle -IdNames @("node_token")
    if ($existingToken) {
        $nodeInfo = Invoke-LarkJson @("wiki", "+node-get", "--node-token", $existingToken)
        $config.wiki_nodes[$childTitle] = [ordered]@{
            node_token = "$existingToken"
            obj_token = "$(Find-FirstValue -Object $nodeInfo.data -Names @("obj_token"))"
            obj_type = "$(Find-FirstValue -Object $nodeInfo.data -Names @("obj_type"))"
        }
    } else {
        $response = Invoke-LarkJson @("wiki", "+node-create", "--parent-node-token", $parentToken, "--title", $childTitle)
        $config.wiki_nodes[$childTitle] = [ordered]@{
            node_token = "$(Find-FirstValue -Object $response.data -Names @("node_token"))"
            obj_token = "$(Find-FirstValue -Object $response.data -Names @("obj_token"))"
            obj_type = "$(Find-FirstValue -Object $response.data -Names @("obj_type"))"
        }
    }
    Save-Config -Config $config
}

$finalTables = Invoke-LarkJson @("base", "+table-list", "--base-token", $config.base_token)
foreach ($name in $tableNames) {
    $verifiedId = Find-NamedId -Object $finalTables.data -ExpectedName $name -IdNames @("table_id", "id")
    if (-not $verifiedId) { throw "最终验证未找到数据表：$name" }
}

Write-Host ""
Write-Host "初始化完成。" -ForegroundColor Green
Write-Host "Base token：$($config.base_token)"
Write-Host "配置文件：$ConfigPath"
Write-Host "下一步：用一条真实材料跑通 收件 → 分析 → 补丁确认 → Wiki 更新 → 验证行动。"
