import React, { useState } from 'react';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, Alert, Linking } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { useSyncStore } from '../store/useSyncStore';

export function ScannerScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const [scannedUrl, setScannedUrl] = useState<string | null>(null);
  
  const [name, setName] = useState('');
  const [cpf, setCpf] = useState('');
  const [plate, setPlate] = useState('');

  const addHandshake = useSyncStore(state => state.addHandshake);

  if (!permission) {
    // Permissões ainda carregando
    return <View style={styles.container} />;
  }

  if (!permission.granted) {
    // Permissão negada ou ainda não solicitada
    return (
      <View style={styles.container}>
        <Text style={styles.message}>Precisamos da sua permissão para usar a câmera e escanear o QR Code da carga.</Text>
        <TouchableOpacity style={styles.primaryButton} onPress={requestPermission}>
          <Text style={styles.primaryButtonText}>Conceder Permissão</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.secondaryButton} onPress={() => Linking.openSettings()}>
          <Text style={styles.secondaryButtonText}>Abrir Ajustes do Celular</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // Trava de Leitura
  const handleBarcodeScanned = ({ type, data }: { type: string; data: string }) => {
    // Pausa imediatamente se já temos um URL (evita loop infinito de reads)
    if (scannedUrl) return; 
    
    // Poderíamos checar aqui se a URL bate com o padrão esperado (ex: agrotrace.com/handshake)
    setScannedUrl(data);
  };

  const handleSubmit = () => {
    if (!name || !cpf || !plate) {
      Alert.alert('Atenção', 'Por favor, preencha todos os campos obrigatórios para assumir a custódia da carga.');
      return;
    }

    // A URL escaneada do papel/carga é a nossa Signed URL
    addHandshake(scannedUrl!, {
      driver_name: name,
      driver_cpf: cpf,
      vehicle_plate: plate,
    });

    // Mágica do Offline
    Alert.alert(
      'Custódia Registrada!',
      'Suas informações foram salvas. A sincronização está rodando em background e será enviada quando houver sinal.',
      [
        {
          text: 'OK',
          onPress: () => {
            // Reset da UI para um possível próximo escaneamento
            setScannedUrl(null);
            setName('');
            setCpf('');
            setPlate('');
          }
        }
      ]
    );
  };

  return (
    <View style={styles.container}>
      {!scannedUrl ? (
        <View style={styles.cameraContainer}>
          <CameraView 
            style={StyleSheet.absoluteFillObject} 
            facing="back"
            onBarcodeScanned={scannedUrl ? undefined : handleBarcodeScanned}
          />
          <View style={styles.overlay}>
            <Text style={styles.overlayText}>Aponte para o QR Code da Carga</Text>
            <View style={styles.scanBox} />
          </View>
        </View>
      ) : (
        <View style={styles.formContainer}>
          <Text style={styles.formTitle}>Identificação</Text>
          <Text style={styles.formSubtitle}>Carga identificada. Por favor, preencha os dados abaixo para assumir a custódia física (Seguro).</Text>
          
          <TextInput
            style={styles.input}
            placeholder="Nome Completo (ex: João da Silva)"
            value={name}
            onChangeText={setName}
            autoCapitalize="words"
            placeholderTextColor="#9ca3af"
          />
          
          <TextInput
            style={styles.input}
            placeholder="CPF (apenas números)"
            value={cpf}
            onChangeText={setCpf}
            keyboardType="number-pad"
            placeholderTextColor="#9ca3af"
          />
          
          <TextInput
            style={styles.input}
            placeholder="Placa do Cavalo Mecânico (ex: ABC1234)"
            value={plate}
            onChangeText={setPlate}
            autoCapitalize="characters"
            placeholderTextColor="#9ca3af"
          />

          <TouchableOpacity style={styles.primaryButtonForm} onPress={handleSubmit}>
            <Text style={styles.primaryButtonText}>Assumir Custódia</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.cancelButton} onPress={() => setScannedUrl(null)}>
            <Text style={styles.cancelButtonText}>Cancelar Leitura</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    backgroundColor: '#18181b', // Fundo escuro para contrastar no sol ao ler permissões
  },
  message: {
    textAlign: 'center',
    paddingBottom: 24,
    fontSize: 18,
    color: '#f4f4f5',
    paddingHorizontal: 20,
    lineHeight: 28,
  },
  cameraContainer: {
    flex: 1,
  },
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.6)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  overlayText: {
    color: '#fff',
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 40,
    textAlign: 'center',
    textShadowColor: 'rgba(0, 0, 0, 0.9)',
    textShadowOffset: { width: -1, height: 1 },
    textShadowRadius: 10
  },
  scanBox: {
    width: 260,
    height: 260,
    borderWidth: 4,
    borderColor: '#3b82f6',
    backgroundColor: 'transparent',
    borderRadius: 16,
  },
  formContainer: {
    flex: 1,
    padding: 24,
    justifyContent: 'center',
    backgroundColor: '#ffffff',
  },
  formTitle: {
    fontSize: 34,
    fontWeight: '900',
    color: '#111827',
    marginBottom: 8,
  },
  formSubtitle: {
    fontSize: 16,
    color: '#4b5563',
    marginBottom: 32,
    lineHeight: 24,
  },
  input: {
    height: 70, // Inputs massivos para dedos grandes/celulares no painel
    borderWidth: 2,
    borderColor: '#e5e7eb',
    borderRadius: 12,
    marginBottom: 16,
    paddingHorizontal: 20,
    fontSize: 20, // Fonte grande para legibilidade à distância
    backgroundColor: '#f9fafb',
    color: '#111827',
  },
  primaryButton: {
    height: 64,
    backgroundColor: '#2563eb',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 20,
  },
  primaryButtonForm: {
    height: 70,
    backgroundColor: '#2563eb',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 16,
    shadowColor: '#2563eb',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  primaryButtonText: {
    color: 'white',
    fontSize: 22,
    fontWeight: '900',
  },
  secondaryButton: {
    height: 64,
    backgroundColor: '#3f3f46',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 16,
    marginHorizontal: 20,
  },
  secondaryButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  cancelButton: {
    height: 64,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 12,
  },
  cancelButtonText: {
    color: '#dc2626',
    fontSize: 18,
    fontWeight: 'bold',
  }
});
