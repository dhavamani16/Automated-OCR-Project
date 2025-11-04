// --- Project Component IV: Flutter Front-End (main.dart) ---
// This file handles the mobile UI, image selection, and communication with the Flask API.

import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:image_picker/image_picker.dart';
import 'package:audioplayers/audioplayers.dart';

// IMPORTANT: Your Python server is running on 127.0.0.1 (localhost) on port 5000.
// On the Android emulator, '10.0.2.2' is the special IP that redirects to the host machine's '127.0.0.1'.
// If testing on a physical phone, you would need to use your specific network IP (like 192.168.x.x).
const String apiUrl = 'http://10.0.2.2:5000/analyze_image';
const String audioBaseUrl = 'http://10.0.2.2:5000'; // Base URL to fetch the audio file

void main() {
  runApp(const OcrTranslatorApp());
}

class OcrTranslatorApp extends StatelessWidget {
  const OcrTranslatorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'OCR Translator',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.indigo,
        visualDensity: VisualDensity.adaptivePlatformVersion,
        textTheme: const TextTheme(
          titleLarge: TextStyle(fontWeight: FontWeight.bold, color: Colors.indigo),
        ),
      ),
      home: const OcrTranslatorScreen(),
    );
  }
}

class OcrTranslatorScreen extends StatefulWidget {
  const OcrTranslatorScreen({super.key});

  @override
  State<OcrTranslatorScreen> createState() => _OcrTranslatorScreenState();
}

class _OcrTranslatorScreenState extends State<OcrTranslatorScreen> {
  File? _imageFile;
  final ImagePicker _picker = ImagePicker();
  bool _isLoading = false;
  String _originalText = '';
  String _translatedText = '';
  String? _audioUrl;
  final AudioPlayer _audioPlayer = AudioPlayer();

  // -----------------------
  // 1. IMAGE PICKING LOGIC
  // -----------------------
  Future<void> _pickImage(ImageSource source) async {
    final pickedFile = await _picker.pickImage(source: source);

    if (pickedFile != null) {
      setState(() {
        _imageFile = File(pickedFile.path);
        // Clear previous results when a new image is selected
        _originalText = '';
        _translatedText = '';
        _audioUrl = null;
      });
      // Automatically analyze the image after picking it
      _analyzeImage(_imageFile!);
    }
  }

  // -----------------------
  // 2. API COMMUNICATION LOGIC
  // -----------------------
  Future<void> _analyzeImage(File image) async {
    setState(() {
      _isLoading = true;
    });

    try {
      // 1. Prepare Multipart Request
      var request = http.MultipartRequest('POST', Uri.parse(apiUrl));
      request.files.add(await http.MultipartFile.fromPath(
        'image', // Field name must match 'image' in app.py
        image.path,
      ));

      // 2. Send Request and Get Response
      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        // 3. Process Success
        final data = json.decode(response.body);
        setState(() {
          _originalText = data['original_text'] ?? 'No original text found.';
          _translatedText = data['translated_text'] ?? 'No translation found.';
          _audioUrl = data['audio_url'];
          print('Audio URL received: $_audioUrl');
        });
      } else {
        // 4. Handle API Error
        final errorData = json.decode(response.body);
        _showError('API Error: ${errorData['message'] ?? 'Unknown error'}');
      }
    } catch (e) {
      // 5. Handle Network/Connection Error
      _showError('Connection Error: Could not reach the Python server at $apiUrl. Ensure your server is running.');
      print('Full Error: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  // -----------------------
  // 3. AUDIO PLAYBACK LOGIC
  // -----------------------
  Future<void> _playAudio() async {
    if (_audioUrl != null && _audioUrl!.isNotEmpty) {
      // Note: The player expects a full URL, which is constructed from audioBaseUrl + relative path
      String fullAudioUrl = '$audioBaseUrl/get_audio'; // Since the server always returns the audio from /get_audio
      await _audioPlayer.play(UrlSource(fullAudioUrl));
    } else {
      _showError('No audio file is available to play.');
    }
  }

  // -----------------------
  // 4. UTILITY & UI METHODS
  // -----------------------
  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }

  Widget _buildResultCard(String title, String content, {bool isTranslated = false}) {
    // Determine the initial message based on whether any content has been received
    String initialMessage = isTranslated 
        ? 'Translation results will appear here.'
        : 'The scanned (OCR) text will appear here.';
    
    // Check if the content is currently empty. If it is, use the initial message.
    String displayContent = content.isEmpty ? initialMessage : content;

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 10),
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: isTranslated ? Colors.indigo : Colors.black87,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              displayContent, // Use the new determined displayContent
              style: const TextStyle(fontSize: 16, color: Colors.black54),
            ),
            if (isTranslated && _audioUrl != null) ...[
              const SizedBox(height: 10),
              ElevatedButton.icon(
                onPressed: _playAudio,
                icon: const Icon(Icons.volume_up),
                label: const Text('Play Translation'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.pink,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
              ),
            ]
          ],
        ),
      ),
    );
  }

  // -----------------------
  // 5. WIDGET BUILDER
  // -----------------------
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('OCR and Voice Translator'),
        backgroundColor: Colors.indigo,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: <Widget>[
            // Image Display
            Container(
              height: 200,
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.indigo.shade300, width: 2),
              ),
              child: Center(
                child: _imageFile == null
                    ? Text('Tap the buttons below to select an image for translation.', style: TextStyle(color: Colors.indigo.shade400))
                    : Image.file(_imageFile!, fit: BoxFit.cover),
              ),
            ),
            const SizedBox(height: 20),

            // Image Selection Buttons
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isLoading ? null : () => _pickImage(ImageSource.camera),
                    icon: const Icon(Icons.camera_alt),
                    label: const Text('Take Photo'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.indigo,
                      padding: const EdgeInsets.symmetric(vertical: 15),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isLoading ? null : () => _pickImage(ImageSource.gallery),
                    icon: const Icon(Icons.photo_library),
                    label: const Text('Select from Gallery'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.deepOrange,
                      padding: const EdgeInsets.symmetric(vertical: 15),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Loading Indicator
            if (_isLoading)
              const Center(child: LinearProgressIndicator(color: Colors.indigo)),

            // Results Display
            _buildResultCard('Original (Simulated OCR) Text:', _originalText),
            _buildResultCard('Translated Text (English):', _translatedText, isTranslated: true),
          ],
        ),
      ),
    );
  }
}
