// Définition des broches des moteurs
#define M1_IN1 2
#define M1_IN2 4
#define M1_PWM 6

#define M2_IN1 12
#define M2_IN2 8
#define M2_PWM 5

// Définition des broches du capteur ultrasonique
#define TRIG_PIN 11
#define ECHO_PIN 10

float lastDistance = -1;  // Stocker la dernière distance envoyée


unsigned long tempsActuel = 0;
unsigned long tempsPrecedent = 0;

const float tempsParDegre = 6.8 / 360.0 * 1000; // Temps en ms par degré

bool enRotation = false;
int dureeRotation = 0; // Durée calculée pour l'angle demandé


void setup() {
    Serial.begin(9600);
    
    // Configuration des broches moteur
    pinMode(M1_IN1, OUTPUT);
    pinMode(M1_IN2, OUTPUT);
    pinMode(M1_PWM, OUTPUT);
    
    pinMode(M2_IN1, OUTPUT);
    pinMode(M2_IN2, OUTPUT);
    pinMode(M2_PWM, OUTPUT);

    // Configuration des broches du capteur
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
}

// Fonction pour contrôler un moteur
void moteur(int in1, int in2, int pwm, int vitesse, bool sens) {
    digitalWrite(in1, sens);
    digitalWrite(in2, !sens);
    analogWrite(pwm, vitesse);
}

// Avancer
void avancer(int vitesse) {
    moteur(M1_IN1, M1_IN2, M1_PWM, vitesse, 1);
    moteur(M2_IN1, M2_IN2, M2_PWM, vitesse, 1);
}

// Reculer
void reculer(int vitesse) {
    moteur(M1_IN1, M1_IN2, M1_PWM, vitesse, 0);
    moteur(M2_IN1, M2_IN2, M2_PWM, vitesse, 0);
}

// Tourner à gauche
void tournerGauche() {
    int vitesse = 200;
    moteur(M1_IN1, M1_IN2, M1_PWM, vitesse, 0);
    moteur(M2_IN1, M2_IN2, M2_PWM, vitesse, 1);
}

// Tourner à droite
void tournerDroite() {
    int vitesse = 200;
    moteur(M1_IN1, M1_IN2, M1_PWM, vitesse, 1);
    moteur(M2_IN1, M2_IN2, M2_PWM, vitesse, 0);
}

void tournerGaucheAngle(int angle) {
    dureeRotation = angle * tempsParDegre; // Calcul du temps nécessaire
    Serial.print("Tourne de ");
    Serial.print(angle);
    Serial.print("° pendant ");
    Serial.print(dureeRotation);
    Serial.println(" ms");
    
    tempsPrecedent = millis();
    enRotation = true;
    tournerGauche();
}

// Arrêter les moteurs
void stopMoteurs() {
    digitalWrite(M1_IN1, LOW);
    digitalWrite(M1_IN2, LOW);
    analogWrite(M1_PWM, 0);

    digitalWrite(M2_IN1, LOW);
    digitalWrite(M2_IN2, LOW);
    analogWrite(M2_PWM, 0);
}

// Mesurer la distance avec le capteur ultrasonique
float mesurerDistance() {
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    long duration = pulseIn(ECHO_PIN, HIGH);
    float distance = (duration * 0.0343) / 2;  // Convertir en cm

    return distance;
}

void loop() {


  delay(2000); // Pause de 2 secondes avant la prochaine rotation
  tournerGaucheAngle(180); // Exécute une rotation de 90° (modifiable)
  delay(2000); // Pause de 2 secondes avant la prochaine rotation
  stopMoteurs();
    
  float distance = mesurerDistance();
  
  // Si la distance change de plus de 1 cm, l'afficher
  if (abs(distance - lastDistance) > 1) {
      Serial.print("Distance : ");
      Serial.print(distance);
      Serial.println(" cm");
  }

  if (distance < 20) {  // Si un obstacle est détecté à moins de 15 cm
      delay(1000); // Pause de 2 secondes avant la prochaine rotation
      tournerGaucheAngle(180); // Exécute une rotation de 90° (modifiable)
      delay(1000);  // Reculer pendant 1 seconde
      stopMoteurs();
      delay(500);
  }
  if (distance < 50) {  // Si un obstacle est détecté à moins de 15 cm
      Serial.println("Obstacle détecté ! Recul...");
      avancer(180);
  } 
    else {
      Serial.println("Aucun obstacle, avance.");
      avancer(200);
  }

  delay(500);  // Petite pause pour éviter trop de mesures rapides
    
}
