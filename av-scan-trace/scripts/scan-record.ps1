param(
    [string]$BaseDir = ''
)

$ErrorActionPreference = 'Continue'

if ($BaseDir -eq '' -or $BaseDir -eq $null) {
    $BaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
}
$BaseDir = $BaseDir.Trim().Trim('"')
$tmpDir = $BaseDir.TrimEnd('\')
if ($tmpDir -match '^[A-Za-z]:$') { $tmpDir = $tmpDir + '\' }
$BaseDir = $tmpDir
if ($BaseDir -eq '') { $BaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path }

# ================= 可调整参数 =================
$Operator  = '中国电信股份有限公司镇江分公司'
$NetType   = '互联网'
$WaitSec   = 2
$FontName  = 'Microsoft YaHei'
$BarHeight = 100
$BarAlpha  = 235
# ==============================================

$shotDir = Join-Path $BaseDir '截图'
if (-not (Test-Path $shotDir)) { New-Item -ItemType Directory -Path $shotDir | Out-Null }
$csvPath = Join-Path $BaseDir '查杀台账.csv'
$refPath = Join-Path $BaseDir '终端对照表.csv'

$hostname = $env:COMPUTERNAME
$now = Get-Date

function Ask([string]$prompt) {
    $v = Read-Host $prompt
    if ($v -eq $null) { $v = '' }
    return $v.Trim()
}

Write-Host ''
Write-Host '====================================================' -ForegroundColor Cyan
Write-Host '  终端木马查杀  现场留痕记录' -ForegroundColor Cyan
Write-Host '====================================================' -ForegroundColor Cyan
Write-Host ''
Write-Host '前置条件：本机已用杀毒软件完成全盘扫描，并停留在扫描结果界面。' -ForegroundColor Gray
Write-Host ''

# ---------- 网卡：找出能上外网的那一个 ----------
$virtPrefix = @('00:50:56', '00:0C:29', '00:05:69', '00:1C:14', '00:15:5D', '00:16:3E', '08:00:27', '52:54:00', '00:1C:42')
$allNic = @()
try {
    $cfgs = Get-WmiObject -Class Win32_NetworkAdapterConfiguration -Filter 'IPEnabled=True' -ErrorAction SilentlyContinue
    if ($cfgs -ne $null) {
        foreach ($c in $cfgs) {
            $ips = @()
            if ($c.IPAddress -ne $null) {
                foreach ($ip in $c.IPAddress) {
                    if ($ip -match '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$' -and $ip -notlike '169.254.*') { $ips += $ip }
                }
            }
            if ($ips.Count -eq 0) { continue }
            $mac = ''
            if ($c.MACAddress -ne $null) { $mac = ([string]$c.MACAddress).Trim() }
            $hasGw = $false
            if ($c.DefaultIPGateway -ne $null -and @($c.DefaultIPGateway).Count -gt 0) { $hasGw = $true }
            $metric = 9999
            try { if ($c.DefaultIPGatewayMetric -ne $null) { $metric = [int](@($c.DefaultIPGatewayMetric)[0]) } } catch { }
            $isVirt = $false
            $mu = $mac.ToUpper()
            foreach ($p in $virtPrefix) { if ($mu.StartsWith($p)) { $isVirt = $true } }
            $allNic += New-Object PSObject -Property @{
                IP = $ips[0]; MAC = $mac; HasGw = $hasGw; Metric = $metric; IsVirt = $isVirt
            }
        }
    }
} catch { }

$primary = $null
$c1 = @($allNic | Where-Object { $_.HasGw -and (-not $_.IsVirt) })
if ($c1.Count -gt 0) { $primary = $c1 | Sort-Object Metric | Select-Object -First 1 }
if ($primary -eq $null) {
    $c2 = @($allNic | Where-Object { $_.HasGw })
    if ($c2.Count -gt 0) { $primary = $c2 | Sort-Object Metric | Select-Object -First 1 }
}
if ($primary -eq $null) {
    $c3 = @($allNic | Where-Object { -not $_.IsVirt })
    if ($c3.Count -gt 0) { $primary = $c3 | Select-Object -First 1 }
}
if ($primary -eq $null -and $allNic.Count -gt 0) { $primary = $allNic[0] }

$ipStr = ''
$macStr = ''
if ($primary -ne $null) { $ipStr = [string]$primary.IP; $macStr = [string]$primary.MAC }

# ---------- 自动检测杀毒软件（仅作默认值） ----------
$avAuto = ''
try {
    $tmpAv = @()
    $avs = Get-WmiObject -Namespace 'root\SecurityCenter2' -Class AntiVirusProduct -ErrorAction SilentlyContinue
    if ($avs -ne $null) {
        foreach ($a in $avs) {
            $nm = ([string]$a.displayName).Trim()
            if ($nm -ne '') { $tmpAv += $nm }
        }
    }
    if ($tmpAv.Count -gt 0) { $avAuto = (@($tmpAv | Select-Object -Unique) -join ' / ') }
} catch { }

# ---------- 读台账（拿已做台数与上次用的查杀工具） ----------
$doneCount = 0
$lastTool = ''
if (Test-Path $csvPath) {
    try {
        $allRows = @(Get-Content -Path $csvPath -Encoding UTF8 | ConvertFrom-Csv)
        $doneCount = $allRows.Count
        if ($doneCount -gt 0) { $lastTool = ([string]$allRows[$doneCount - 1].'查杀工具').Trim() }
    } catch { $doneCount = 0 }
}
$autoNo = '{0:D3}' -f ($doneCount + 1)

# ---------- 读对照表 ----------
$ref = @()
$refOk = $false
if (Test-Path $refPath) {
    try {
        $ref = @(Get-Content -Path $refPath -Encoding UTF8 | ConvertFrom-Csv)
        $refOk = $true
    } catch { $refOk = $false }
}

# ---------- 显示本机信息 ----------
Write-Host ('计算机名 : ' + $hostname)
if ($primary -ne $null) {
    Write-Host ('上网网卡 : ' + $ipStr + '    ' + $macStr)
} else {
    Write-Host '上网网卡 : 未识别到可用网卡' -ForegroundColor Yellow
}
if ($allNic.Count -gt 1) {
    $others = @()
    foreach ($n in $allNic) {
        if ($primary -ne $null -and [string]$n.IP -eq [string]$primary.IP) { continue }
        $others += ([string]$n.IP + ' ' + [string]$n.MAC)
    }
    if ($others.Count -gt 0) { Write-Host ('其他网卡 : ' + ($others -join '  |  ')) -ForegroundColor DarkGray }
}
if ($avAuto -ne '') { Write-Host ('自动检测 : ' + $avAuto) -ForegroundColor DarkGray }
if (-not $refOk) { Write-Host '提示：未找到 终端对照表.csv，门牌号无法自动匹配部门。' -ForegroundColor Yellow }
Write-Host ''

# ---------- 门牌号 -> 部门 ----------
$room = ''
while ($room -eq '') {
    $room = Ask '请输入门牌号（如 301）'
    if ($room -eq '') { Write-Host '  门牌号不能为空。' -ForegroundColor Yellow }
}

$depts = @()
if ($refOk) {
    foreach ($r in $ref) {
        if (([string]$r.room).Trim() -eq $room) {
            $dp = ([string]$r.dept).Trim()
            if ($dp -ne '' -and $depts -notcontains $dp) { $depts += $dp }
        }
    }
}

$dept = ''
if ($depts.Count -eq 1) {
    Write-Host ('          ' + $room + '  对应部门  ' + $depts[0]) -ForegroundColor Green
    $ans = Ask ('部门（回车 = ' + $depts[0] + '）')
    if ($ans -eq '') { $dept = $depts[0] } else { $dept = $ans }
} elseif ($depts.Count -gt 1) {
    Write-Host '  该门牌号在对照表中对应多个部门：' -ForegroundColor Yellow
    for ($i = 0; $i -lt $depts.Count; $i++) { Write-Host ('    ' + ($i + 1) + ') ' + $depts[$i]) }
    $sel = Ask ('请选择序号（回车 = 1）')
    $n = 1
    if ($sel -ne '') { try { $n = [int]$sel } catch { $n = 1 } }
    if ($n -lt 1 -or $n -gt $depts.Count) { $n = 1 }
    $dept = $depts[$n - 1]
} else {
    Write-Host ('  对照表中没有门牌号 ' + $room) -ForegroundColor Yellow
    $dept = Ask '部门（可留空）'
}

$user = Ask '使用人（可留空）'

# ---------- 查杀工具 ----------
$toolDefault = ''
if ($lastTool -ne '') { $toolDefault = $lastTool } elseif ($avAuto -ne '') { $toolDefault = $avAuto }
if ($toolDefault -ne '') {
    $tool = Ask ('查杀工具（回车 = ' + $toolDefault + '）')
    if ($tool -eq '') { $tool = $toolDefault }
} else {
    $tool = Ask '查杀工具（如 火绒安全软件）'
}
if ($tool -eq '') { $tool = '未记录' }

# ---------- 检测结果 / 处置结果 ----------
$pick = Ask '检测结果   1=发现木马   2=未发现异常（回车 = 2）'
if ($pick -eq '1') {
    $resultText = '发现木马'
    $dispoText = '清除成功'
    $threat = Ask '检出木马名称（可留空，会写入备注）'
    $remark = ''
    if ($threat -ne '') { $remark = '检出：' + $threat }
} else {
    $resultText = '未发现异常'
    $dispoText = '正常'
    $remark = ''
}

Write-Host ''
Write-Host '----------------------------------------------------' -ForegroundColor DarkGray
Write-Host ('编号 ' + $autoNo + '   门牌号 ' + $room + '   部门 ' + $dept)
Write-Host ('使用人 ' + $user + '   工具 ' + $tool + '   结果 ' + $resultText + '   处置 ' + $dispoText)
Write-Host '----------------------------------------------------' -ForegroundColor DarkGray

# ---------- 提示 + 回车 ----------------
Write-Host ''
Write-Host '请确认杀毒软件的扫描结果界面已在屏幕上完整可见。' -ForegroundColor Yellow
Write-Host '界面里要能看到病毒库版本或更新时间。' -ForegroundColor Yellow
Write-Host ''
Write-Host ('确认无误后按回车。本窗口会自动最小化，' + $WaitSec + ' 秒后截屏。') -ForegroundColor Green
$null = Read-Host

# ---------- 截屏 ----------
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$code = @'
using System;
using System.Runtime.InteropServices;
public class TraceHelper {
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("kernel32.dll")] public static extern IntPtr GetConsoleWindow();
}
'@
try { Add-Type -TypeDefinition $code -ErrorAction SilentlyContinue } catch { }
try { [TraceHelper]::SetProcessDPIAware() | Out-Null } catch { }

$hWnd = [IntPtr]::Zero
try { $hWnd = [TraceHelper]::GetConsoleWindow() } catch { }
try { [TraceHelper]::ShowWindow($hWnd, 6) | Out-Null } catch { }
Start-Sleep -Seconds $WaitSec

$bounds = [System.Windows.Forms.SystemInformation]::VirtualScreen
$bmp = New-Object System.Drawing.Bitmap($bounds.Width, $bounds.Height)
$gfx = [System.Drawing.Graphics]::FromImage($bmp)
try {
    $gfx.CopyFromScreen($bounds.X, $bounds.Y, 0, 0, $bounds.Size)
} catch {
    Start-Sleep -Seconds 3
    try { $gfx.CopyFromScreen($bounds.X, $bounds.Y, 0, 0, $bounds.Size) } catch { }
}

# ---------- 水印条 ----------
$scale = $bounds.Height / 1080.0
if ($scale -lt 1) { $scale = 1 }
$barH = [int]($BarHeight * $scale)
$fs1 = [int](24 * $scale)
$fs2 = [int](15 * $scale)
$timeStr = $now.ToString('yyyy-MM-dd HH:mm:ss')

$line1 = '编号 ' + $autoNo + '    门牌号 ' + $room + '    计算机名 ' + $hostname
$line2 = 'IP ' + $ipStr + '    时间 ' + $timeStr + '    执行方 ' + $Operator

try {
    $barBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb($BarAlpha, 0, 0, 0))
    $gfx.FillRectangle($barBrush, 0, 0, $bounds.Width, $barH)
    $f1 = New-Object System.Drawing.Font($FontName, $fs1, [System.Drawing.FontStyle]::Bold)
    $f2 = New-Object System.Drawing.Font($FontName, $fs2)
    $gfx.DrawString($line1, $f1, [System.Drawing.Brushes]::White, 24, [int](10 * $scale))
    $gfx.DrawString($line2, $f2, [System.Drawing.Brushes]::White, 26, [int]($barH - $fs2 * 2.2))
} catch { }
try { $gfx.Dispose() } catch { }

# ---------- 保存截图 ----------
$stamp = $now.ToString('yyyyMMdd_HHmmss')
$fileName = $autoNo + '_' + $room + '_' + $hostname + '_' + $stamp + '.png'
$savePath = Join-Path $shotDir $fileName
$saved = $false
try {
    $bmp.Save($savePath, [System.Drawing.Imaging.ImageFormat]::Png)
    $saved = $true
} catch { }

# ---------- 写台账 ----------
function Esc([string]$s) {
    if ($s -eq $null) { $s = '' }
    $s = $s -replace "`r", ' '
    $s = $s -replace "`n", ' '
    return '"' + ($s -replace '"', '""') + '"'
}
$header = '门牌号,部门,使用人,网络类型,IP地址,MAC地址,hostname,排查时间,查杀工具,检测结果,处置结果,截图文件,备注'
$cols = @($room, $dept, $user, $NetType, $ipStr, $macStr, $hostname, $timeStr, $tool, $resultText, $dispoText, $fileName, $remark)
$cells = @()
foreach ($c in $cols) { $cells += (Esc $c) }
$rowLine = $cells -join ','

if ($saved) {
    if (-not (Test-Path $csvPath)) { Add-Content -Path $csvPath -Value $header -Encoding UTF8 }
    Add-Content -Path $csvPath -Value $rowLine -Encoding UTF8
}

try { $bmp.Dispose() } catch { }
try { [TraceHelper]::ShowWindow($hWnd, 9) | Out-Null } catch { }

Write-Host ''
if ($saved) {
    Write-Host '本台记录完成。' -ForegroundColor Green
    Write-Host ('截图 : ' + $savePath) -ForegroundColor Green
    Write-Host ('台账 : ' + $csvPath) -ForegroundColor Green
} else {
    Write-Host '截图保存失败，本台未写入台账，请重跑。' -ForegroundColor Red
}
Write-Host ''
Write-Host '关闭本窗口，继续下一台。' -ForegroundColor Gray
