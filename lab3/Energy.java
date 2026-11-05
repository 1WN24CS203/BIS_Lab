abstract class EnergySource {
    protected String sourceId;
    protected String sourceName;
    protected double energyGenerated; 

    public EnergySource(String sourceId, String sourceName, double energyGenerated) 
    {
        this.sourceId = sourceId;
        this.sourceName = sourceName;
        this.energyGenerated = energyGenerated;
    }

    public abstract double calculateEfficiency();

    public void displayDetails() {
        System.out.println("Source ID        : " + sourceId);
        System.out.println("Source Name      : " + sourceName);
        System.out.println("Energy Generated : " + energyGenerated + " kWh");
        System.out.printf("Efficiency       : %.2f%%\n", calculateEfficiency());
        System.out.println("------------------------------------");
    }
}

class SolarEnergy extends EnergySource {
    public SolarEnergy(String sourceId, String sourceName, double energyGenerated) {
        super(sourceId, sourceName, energyGenerated);
    }

    @Override
    public double calculateEfficiency() {
        return (energyGenerated / 5000.0) * 100;
    }
}

class WindEnergy extends EnergySource {
    public WindEnergy(String sourceId, String sourceName, double energyGenerated) {
        super(sourceId, sourceName, energyGenerated);
    }

    @Override
    public double calculateEfficiency() {
        return (energyGenerated / 8000.0) * 100;
    }
}

public class EnergyManagement {
    public static void main(String[] args) {
        // Declaring an EnergySource reference
        EnergySource sourceRef;


        sourceRef = new SolarEnergy("101", "Solar", 3800.0);
        sourceRef.displayDetails(); 

        sourceRef = new WindEnergy("100", "Wind Turbine", 5200.0);
        sourceRef.displayDetails(); 
    }
}
