# PowerShell Document Upload Example
$uri = "http://localhost:8000/upload"
$filePath = "data\uploads\vendor_invoices\sample_invoice_abc_coffee_20240115.txt"

# Create form data
$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

$bodyLines = (
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"$(Split-Path $filePath -Leaf)`"",
    "Content-Type: text/plain$LF",
    (Get-Content $filePath -Raw),
    "--$boundary",
    "Content-Disposition: form-data; name=`"doc_type`"$LF",
    "auto_detect",
    "--$boundary--$LF"
) -join $LF

# Upload the file
try {
    $response = Invoke-RestMethod -Uri $uri -Method Post -Body $bodyLines -ContentType "multipart/form-data; boundary=$boundary"
    Write-Host "✅ Upload successful!" -ForegroundColor Green
    Write-Host "📄 File ID: $($response.data.file_id)" -ForegroundColor Cyan
    Write-Host "📋 Document type: $($response.data.doc_type)" -ForegroundColor Yellow
} catch {
    Write-Host "❌ Upload failed: $($_.Exception.Message)" -ForegroundColor Red
}