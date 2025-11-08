import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:audioplayers/audioplayers.dart';
import 'dart:io';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:convert';
import 'dart:typed_data';
import 'dart:async';
import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';

// Port the local Python server is running on. Leave this alone unless your
// server uses a different port.
const int _apiPort = 5000;

// Note: when running on Android emulator (default AVD) the host machine's
// localhost is reachable at 10.0.2.2. On iOS simulator and desktop/web, use
// 127.0.0.1. On a physical device, use your PC's LAN IP (e.g. 192.168.x.y)
// and make sure the Python server binds to 0.0.0.0.

void main() {
  runApp(const OcrTranslatorApp());
}

class OcrTranslatorApp extends StatelessWidget {
  const OcrTranslatorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'OCR and Voice Translator',
      theme: ThemeData(
        primarySwatch: Colors.indigo,
        visualDensity: VisualDensity.adaptivePlatformDensity,
        scaffoldBackgroundColor: Colors.indigo.shade50,
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
  String _extractedText = 'Please pick an image to start OCR.';
  String _translatedText = '';
  String _targetLanguage = 'es'; // Default to Spanish
  bool _isLoading = false;

  final ImagePicker _picker = ImagePicker();
  final AudioPlayer _audioPlayer = AudioPlayer();

  // Computed API URL based on platform/emulator/device
  late final String _apiUrl;

  // List of supported languages for translation and TTS
  final Map<String, String> _languages = const {
    'English': 'en',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Italian': 'it',
    'Portuguese': 'pt',
    'Chinese': 'zh',
  };

  @override
  void initState() {
    super.initState();
    _apiUrl = _computeApiUrl();
    // Helpful debug print - remove in production
    print('Using API URL: $_apiUrl');
  }

  String _computeApiUrl() {
    // If running in a browser, localhost works for dev server.
    if (kIsWeb) return 'http://127.0.0.1:$_apiPort';

    try {
      if (Platform.isAndroid) {
        // Android emulator (AVD) maps host localhost to 10.0.2.2
        return 'http://10.0.2.2:$_apiPort';
      }
      if (Platform.isIOS) {
        // iOS simulator can use localhost
        return 'http://127.0.0.1:$_apiPort';
      }
    } catch (e) {
      // Platform not available or unknown; fall back to localhost
    }

    // Default fallback (also works when testing on desktop)
    return 'http://127.0.0.1:$_apiPort';
  }

  // Simple POST with timeout and a couple retries for transient network issues
  Future<http.Response> _postWithRetry(Uri uri, String body, {int retries = 2}) async {
    int attempt = 0;
    while (true) {
      attempt++;
      try {
        final resp = await http.post(uri, headers: {'Content-Type': 'application/json'}, body: body).timeout(const Duration(seconds: 20));
        return resp;
      } on TimeoutException catch (e) {
        if (attempt >= retries) rethrow;
        await Future.delayed(const Duration(milliseconds: 800));
      } on SocketException catch (e) {
        if (attempt >= retries) rethrow;
        await Future.delayed(const Duration(milliseconds: 800));
      }
    }
  }

  Future<void> _extractTextFromImage(ImageSource source) async {
    setState(() {
      _isLoading = true;
      _extractedText = 'Processing image...';
      _translatedText = '';
    });

    try {
      final XFile? pickedFile = await _picker.pickImage(source: source);

      if (pickedFile == null) {
        setState(() {
          _isLoading = false;
          _extractedText = 'Image picking cancelled.';
        });
        return;
      }

      // Read the file as bytes (necessary for web/server upload)
      final Uint8List bytes = await pickedFile.readAsBytes();

      String extracted = '';

      // Try on-device OCR first (skip on web where ML Kit isn't available)
      if (!kIsWeb) {
        try {
          final inputImage = InputImage.fromFilePath(pickedFile.path);
          final textRecognizer = TextRecognizer();
          final RecognizedText recognised = await textRecognizer.processImage(inputImage);
          extracted = recognised.text.trim();
          await textRecognizer.close();
          // Debug print
          print('On-device OCR extracted: "$extracted"');
        } catch (e) {
          // If on-device OCR fails for any reason, log and fall back to server
          print('On-device OCR failed: $e');
          extracted = '';
        }
      }

      // If on-device OCR didn't find text, upload to server as base64 fallback
      if (extracted.isEmpty) {
        final String base64Image = base64Encode(bytes);
        final response = await _postWithRetry(
          Uri.parse('$_apiUrl/ocr'),
          json.encode({
            'image': base64Image, // Key must match 'image' expected by app.py
          }),
        );

        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          extracted = (data['extracted_text'] ?? '').toString().trim();
        } else {
          print('Server Response Body on Error: ${response.body}');
          throw Exception('Failed to extract text. Server error: ${response.statusCode}');
        }
      }
      // *** END FIX ***

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final String extracted = data['extracted_text'] ?? 'No text found.';
        setState(() {
          _extractedText = extracted.trim();
        });
        await _translateText(extracted);
      } else {
        // Log the response body for better debugging of server errors
        print('Server Response Body on Error: ${response.body}');
        throw Exception('Failed to extract text. Server error: ${response.statusCode}');
      }
    } catch (e) {
      setState(() {
        _extractedText = 'Error during OCR: $e';
        _translatedText = '';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _translateText(String text) async {
    if (text.isEmpty || text == 'No text found.') {
      setState(() => _translatedText = '');
      return;
    }

    setState(() {
      _translatedText = 'Translating...';
      _isLoading = true;
    });

    try {
      final response = await _postWithRetry(
        Uri.parse('$_apiUrl/translate'),
        json.encode({
          'text': text,
          'target_lang': _targetLanguage,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _translatedText = data['translated_text'] ?? 'Translation failed.';
        });
      } else {
        throw Exception('Failed to translate text. Server error: ${response.statusCode}');
      }
    } catch (e) {
      setState(() {
        _translatedText = 'Error during translation: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _textToSpeech(String text) async {
    if (text.isEmpty) return;

    setState(() {
      _isLoading = true;
    });

    try {
      // NOTE: We use the translated text and the target language for TTS
      final response = await _postWithRetry(
        Uri.parse('$_apiUrl/tts'),
        json.encode({
          'text': text,
          'lang': _targetLanguage,
        }),
      );

      if (response.statusCode == 200) {
        // The response body is the raw MP3 data
        final Uint8List audioBytes = response.bodyBytes;
        final String fullAudioUrl = Uri.dataFromBytes(
          audioBytes,
          mimeType: 'audio/mp3',
        ).toString();

        await _audioPlayer.play(UrlSource(fullAudioUrl));
      } else {
        throw Exception('Failed to get audio. Server error: ${response.statusCode}');
      }
    } catch (e) {
      // Log the error for debugging
      print('TTS Error: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('OCR and Voice Translator', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.indigo,
        elevation: 4,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            // --- Language Selector and Action Buttons ---
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                DropdownButton<String>(
                  value: _targetLanguage,
                  icon: const Icon(Icons.translate, color: Colors.indigo),
                  elevation: 16,
                  style: const TextStyle(color: Colors.indigo, fontSize: 16),
                  underline: Container(height: 2, color: Colors.indigoAccent),
                  onChanged: (String? newValue) {
                    setState(() {
                      _targetLanguage = newValue!;
                      // Re-translate immediately if there is extracted text
                      if (_extractedText.isNotEmpty && _extractedText != 'Please pick an image to start OCR.') {
                        _translateText(_extractedText);
                      }
                    });
                  },
                  items: _languages.entries.map<DropdownMenuItem<String>>((MapEntry<String, String> entry) {
                    return DropdownMenuItem<String>(
                      value: entry.value,
                      child: Text('Translate to ${entry.key}'),
                    );
                  }).toList(),
                ),
                ElevatedButton.icon(
                  onPressed: _isLoading
                      ? null
                      : () => _textToSpeech(_translatedText.isEmpty ? _extractedText : _translatedText),
                  icon: const Icon(Icons.volume_up),
                  label: const Text('Read Text'),
                  style: ElevatedButton.styleFrom(
                    foregroundColor: Colors.white, backgroundColor: Colors.indigo,
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // --- Image Picker Buttons ---
            Center(
              child: Wrap(
                spacing: 16.0,
                runSpacing: 16.0,
                children: [
                  _buildActionButton(
                    icon: Icons.camera_alt,
                    label: 'Take Photo',
                    onPressed: _isLoading
                        ? null
                        : () => _extractTextFromImage(ImageSource.camera),
                  ),
                  _buildActionButton(
                    icon: Icons.image,
                    label: 'Pick from Gallery',
                    onPressed: _isLoading
                        ? null
                        : () => _extractTextFromImage(ImageSource.gallery),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 30),

            // --- Extracted Text Display ---
            _buildResultCard(
              title: 'Extracted Text (Original)',
              content: _extractedText,
              isLoading: _isLoading && _extractedText == 'Processing image...',
              icon: Icons.document_scanner,
            ),
            const SizedBox(height: 20),

            // --- Translated Text Display ---
            _buildResultCard(
              title: 'Translated Text (Target Language)',
              content: _translatedText,
              isLoading: _isLoading && _translatedText == 'Translating...',
              icon: Icons.g_translate,
            ),
          ],
        ),
      ),
    );
  }

  // Helper widget for action buttons
  Widget _buildActionButton({
    required IconData icon,
    required String label,
    VoidCallback? onPressed,
  }) {
    return SizedBox(
      width: 150,
      height: 60,
      child: ElevatedButton.icon(
        onPressed: onPressed,
        icon: Icon(icon),
        label: Text(label),
        style: ElevatedButton.styleFrom(
          foregroundColor: Colors.indigo,
          backgroundColor: Colors.white,
          side: const BorderSide(color: Colors.indigo, width: 2),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          elevation: 4,
        ),
      ),
    );
  }

  // Helper widget for results display cards
  Widget _buildResultCard({
    required String title,
    required String content,
    required bool isLoading,
    required IconData icon,
  }) {
    return Card(
      elevation: 6,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: Colors.indigo, size: 24),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.indigo.shade800,
                  ),
                ),
              ],
            ),
            const Divider(color: Colors.indigoAccent),
            const SizedBox(height: 8),
            isLoading
                ? const Center(child: CircularProgressIndicator(color: Colors.indigo))
                : Text(
                    content.isEmpty ? 'Awaiting action...' : content,
                    style: TextStyle(fontSize: 16, color: Colors.grey.shade700, height: 1.5),
                  ),
          ],
        ),
      ),
    );
  }
}