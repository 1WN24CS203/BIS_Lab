
interface ParkingCharge {
double calculateCharge();
void displayParkingDetails();
}

// Base class containing vehicle metadata
class VehicleParking {
protected String vehicleNumber;
protected String vehicleType;
protected double parkingHours;

public VehicleParking(String vehicleNumber, String vehicleType, double parkingHours) {
this.vehicleNumber = vehicleNumber;
this.vehicleType = vehicleType;
this.parkingHours = parkingHours;
 }
}

// Derived class TwoWheeler implementing the ParkingCharge interface
class TwoWheeler extends VehicleParking implements ParkingCharge {
 public TwoWheeler(String vehicleNumber, double parkingHours) {
super(vehicleNumber, "Two-Wheeler", parkingHours);
 }

 @Override
 public double calculateCharge() {
 if (parkingHours <= 2) {
return parkingHours * 20;
 } else {
return (2 * 20) + ((parkingHours - 2) * 10);
}
}

@Override
 public void displayParkingDetails() {
 System.out.println("Vehicle Number  : " + vehicleNumber);
 System.out.println("Vehicle Type    : " + vehicleType);
 System.out.println("Parking Duration: " + parkingHours + " hours");
 System.out.println("Total Charge    : Rs. " + calculateCharge());
 System.out.println("------------------------------------");
 }
}

// Derived class FourWheeler implementing the ParkingCharge interface
class FourWheeler extends VehicleParking implements ParkingCharge {
 public FourWheeler(String vehicleNumber, double parkingHours) {
super(vehicleNumber, "Four-Wheeler", parkingHours);
 }

 @Override
 public double calculateCharge() {
 if (parkingHours <= 2) {
        return parkingHours * 50;
} else {
 return (2 * 50) + ((parkingHours - 2) * 30);
 }
 }

 @Override
public void displayParkingDetails() {
System.out.println("Vehicle Number  : " + vehicleNumber);
 System.out.println("Vehicle Type    : " + vehicleType);
 System.out.println("Parking Duration: " + parkingHours + " hours");
 System.out.println("Total Charge    : Rs. " + calculateCharge());
 System.out.println("------------------------------------");
 }
}

// Main class demonstrating Interface Runtime Polymorphism
public class ParkingSystem {
public static void main(String[] args) {

 ParkingCharge chargeRef;

System.out.println("=== Demonstrating Runtime Polymorphism via Interface ===\n");


chargeRef = new TwoWheeler("KA-01-HE-1234", 4.5);
chargeRef.displayParkingDetails(); // Polymorphic invocation

 chargeRef = new FourWheeler("DL-03-CC-5678", 1.5);
 chargeRef.displayParkingDetails(); // Polymorphic invocation
 }
}


