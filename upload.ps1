function Run-Command {
    param(
        [string]$command
    )
    try {
        $command
    }
    catch {
        Write-Host "Error running command: $command"
        Write-Host $_.Exception.Message
        return $false
    }
    return $true
}

# 执行构建命令
if (-not (Run-Command "hatch build")) {
    Write-Host "Build failed. Stopping."
}
elseif (-not (Run-Command "twine check dist/*")) {
    Write-Host "Check failed. Not uploading."
}
else {
    # 上传文件
    Run-Command "twine upload dist/*"
}
