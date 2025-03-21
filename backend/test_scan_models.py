from app.models.scan import ScanCreate, ScanType

def test_scan_create():
    """Test the ScanCreate class."""
    scan = ScanCreate(
        name="Test Scan",
        target="127.0.0.1",
        scan_type=ScanType.NETWORK
    )
    print(f"Created scan: {scan.model_dump()}")
    
if __name__ == "__main__":
    test_scan_create() 