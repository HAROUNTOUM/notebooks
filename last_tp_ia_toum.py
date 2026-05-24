from aima3.logic import FolKB, expr, fol_fc_ask, fol_bc_ask
from collections import defaultdict

class MedicalDiagnosticSystem:
    def __init__(self):
        self.knowledge_base = FolKB()
        self._initialize_disease_symptoms()
        self._add_patient_data()

    def _initialize_disease_symptoms(self):
        """Define symptom-disease relationships"""
        symptom_rules = [
            "Cough(x) & RunnyNose(x) & SoreThroat(x) ==> HasDisease(x, Cold)",
            "Fever(x) & Headache(x) & Cough(x) & Fatigue(x) ==> HasDisease(x, Flu)",
            "Fever(x) & Nausea(x) & Vomiting(x) ==> HasDisease(x, FoodPoisoning)",
            "Fever(x) & Cough(x) & ShortnessOfBreath(x) & Fatigue(x) ==> HasDisease(x, COVID19)",
            "Headache(x) & Nausea(x) & Fatigue(x) ==> HasDisease(x, Migraine)",
            "Fever(x) & SoreThroat(x) & Headache(x) ==> HasDisease(x, StrepThroat)",
            "Cough(x) & ShortnessOfBreath(x) & Fatigue(x) ==> HasDisease(x, Pneumonia)",
            "RunnyNose(x) & Cough(x) & SoreThroat(x) ==> HasDisease(x, Allergy)"
        ]
        
        for rule in symptom_rules:
            self.knowledge_base.tell(expr(rule))

    def _add_patient_data(self):
        """Add patient symptoms to the knowledge base"""
        patient_symptoms = {
            "Ali": ["Cough", "RunnyNose", "SoreThroat"],
            "Sara": ["Fever", "Headache", "Cough", "Fatigue"],
            "Omar": ["Fever", "SoreThroat", "Headache"],
            "Lina": ["Headache", "Nausea", "Fatigue"],
            "Hassan": ["Cough", "RunnyNose", "SoreThroat"]
        }
        
        for patient, symptoms in patient_symptoms.items():
            for symptom in symptoms:
                self.knowledge_base.tell(expr(f"{symptom}({patient})"))

    def _process_query_results(self, results):
        """Group query results by patient"""
        x_var = expr("x")
        y_var = expr("y")
        grouped_results = defaultdict(set)

        for entry in results:
            if x_var in entry and y_var in entry:
                grouped_results[entry[x_var]].add(entry[y_var])

        return {patient: list(diseases) for patient, diseases in grouped_results.items()}

    def diagnose_with_forward_chaining(self):
        """Perform diagnosis using forward chaining"""
        print("Diagnostics (using Forward Chaining):")
        results = list(fol_fc_ask(self.knowledge_base, expr("HasDisease(x, y)")))
        diagnosis = self._process_query_results(results)
        
        for patient, diseases in diagnosis.items():
            print(f"{patient}: {diseases}")

    def diagnose_with_backward_chaining(self):
        """Perform diagnosis using backward chaining"""
        print("\nDiagnostics (using Backward Chaining):")
        results = list(fol_bc_ask(self.knowledge_base, expr("HasDisease(x, y)")))
        diagnosis = self._process_query_results(results)
        
        for patient, diseases in diagnosis.items():
            print(f"{patient}: {diseases}")

    def run_diagnostics(self):
        """Run both diagnostic methods"""
        self.diagnose_with_forward_chaining()
        self.diagnose_with_backward_chaining()


if __name__ == "__main__":
    diagnostic_system = MedicalDiagnosticSystem()
    diagnostic_system.run_diagnostics()