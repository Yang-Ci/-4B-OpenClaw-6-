#include <windows.h>
#include <mmdeviceapi.h>
#include <audioclient.h>
#include <stdio.h>
#include <conio.h>
#include <thread>
#include <atomic>
#include <vector>
#include <cstring>

#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "uuid.lib")

const int TARGET_SAMPLE_RATE = 16000;
const int TARGET_CHANNELS = 1;
const int BITS_PER_SAMPLE = 16;
const int TARGET_BLOCK_ALIGN = TARGET_CHANNELS * BITS_PER_SAMPLE / 8;
const int TARGET_BYTE_RATE = TARGET_SAMPLE_RATE * TARGET_BLOCK_ALIGN;

struct WAVHeader {
    char riff[4] = {'R', 'I', 'F', 'F'};
    DWORD fileSize;
    char wave[4] = {'W', 'A', 'V', 'E'};
    char fmt[4] = {'f', 'm', 't', ' '};
    DWORD fmtSize = 16;
    WORD audioFormat = 1;
    WORD numChannels = TARGET_CHANNELS;
    DWORD sampleRate = TARGET_SAMPLE_RATE;
    DWORD byteRate = TARGET_BYTE_RATE;
    WORD blockAlign = TARGET_BLOCK_ALIGN;
    WORD bitsPerSample = BITS_PER_SAMPLE;
    char data[4] = {'d', 'a', 't', 'a'};
    DWORD dataSize;
};

class AudioRecorder {
private:
    IMMDeviceEnumerator* pEnumerator = nullptr;
    IMMDevice* pDevice = nullptr;
    IAudioClient* pAudioClient = nullptr;
    IAudioCaptureClient* pCaptureClient = nullptr;
    WAVEFORMATEX* pDeviceFormat = nullptr;
    
    std::atomic<bool> isRecording{false};
    std::atomic<bool> shouldStop{false};
    std::vector<BYTE> audioData;
    std::vector<BYTE> tempBuffer;
    std::thread recordThread;
    
    int deviceSampleRate = 0;
    int deviceChannels = 0;

public:
    ~AudioRecorder() {
        Cleanup();
    }

    bool Initialize() {
        HRESULT hr = CoInitializeEx(nullptr, COINIT_MULTITHREADED);
        if (FAILED(hr)) {
            printf("COM初始化失败: 0x%08X\n", hr);
            return false;
        }

        hr = CoCreateInstance(
            __uuidof(MMDeviceEnumerator),
            nullptr,
            CLSCTX_ALL,
            __uuidof(IMMDeviceEnumerator),
            (void**)&pEnumerator
        );
        if (FAILED(hr)) {
            printf("创建设备枚举器失败: 0x%08X\n", hr);
            return false;
        }

        hr = pEnumerator->GetDefaultAudioEndpoint(eCapture, eConsole, &pDevice);
        if (FAILED(hr)) {
            printf("获取默认音频设备失败: 0x%08X\n", hr);
            return false;
        }

        hr = pDevice->Activate(__uuidof(IAudioClient), CLSCTX_ALL, nullptr, (void**)&pAudioClient);
        if (FAILED(hr)) {
            printf("激活音频客户端失败: 0x%08X\n", hr);
            return false;
        }

        hr = pAudioClient->GetMixFormat(&pDeviceFormat);
        if (FAILED(hr)) {
            printf("获取音频格式失败: 0x%08X\n", hr);
            return false;
        }

        deviceSampleRate = pDeviceFormat->nSamplesPerSec;
        deviceChannels = pDeviceFormat->nChannels;
        
        printf("设备音频格式: %d Hz, %d 声道, %d 位\n", 
               deviceSampleRate, deviceChannels, pDeviceFormat->wBitsPerSample);

        hr = pAudioClient->Initialize(
            AUDCLNT_SHAREMODE_SHARED,
            0,
            10000000,
            0,
            pDeviceFormat,
            nullptr
        );
        if (FAILED(hr)) {
            printf("初始化音频客户端失败: 0x%08X\n", hr);
            return false;
        }

        hr = pAudioClient->GetService(__uuidof(IAudioCaptureClient), (void**)&pCaptureClient);
        if (FAILED(hr)) {
            printf("获取捕获客户端失败: 0x%08X\n", hr);
            return false;
        }

        return true;
    }

    void StartRecording() {
        if (isRecording) {
            printf("录音已经在进行中...\n");
            return;
        }

        audioData.clear();
        shouldStop = false;
        isRecording = true;

        HRESULT hr = pAudioClient->Start();
        if (FAILED(hr)) {
            printf("开始录音失败: 0x%08X\n", hr);
            isRecording = false;
            return;
        }

        recordThread = std::thread(&AudioRecorder::RecordLoop, this);
        printf("开始录音...\n");
    }

    void StopRecording() {
        if (!isRecording) {
            printf("当前没有在录音\n");
            return;
        }

        shouldStop = true;
        if (recordThread.joinable()) {
            recordThread.join();
        }

        if (pAudioClient) {
            pAudioClient->Stop();
        }

        isRecording = false;
        printf("录音已停止\n");
    }

    void SaveToWAV(const char* filename) {
        if (audioData.empty()) {
            printf("没有录音数据可保存\n");
            return;
        }

        FILE* file = nullptr;
        fopen_s(&file, filename, "wb");
        if (!file) {
            printf("无法创建文件: %s\n", filename);
            return;
        }

        WAVHeader header;
        header.dataSize = static_cast<DWORD>(audioData.size());
        header.fileSize = sizeof(WAVHeader) + header.dataSize - 8;

        fwrite(&header, sizeof(WAVHeader), 1, file);
        fwrite(audioData.data(), 1, audioData.size(), file);
        fclose(file);

        printf("录音已保存到: %s\n", filename);
    }

    bool IsRecording() const {
        return isRecording;
    }

    void Cleanup() {
        if (pCaptureClient) {
            pCaptureClient->Release();
            pCaptureClient = nullptr;
        }
        if (pAudioClient) {
            pAudioClient->Release();
            pAudioClient = nullptr;
        }
        if (pDeviceFormat) {
            CoTaskMemFree(pDeviceFormat);
            pDeviceFormat = nullptr;
        }
        if (pDevice) {
            pDevice->Release();
            pDevice = nullptr;
        }
        if (pEnumerator) {
            pEnumerator->Release();
            pEnumerator = nullptr;
        }
        CoUninitialize();
    }

private:
    // 音频处理：重采样和格式转换
    void ProcessAudio(const BYTE* input, size_t inputBytes, std::vector<BYTE>& output) {
        WORD formatTag = pDeviceFormat->wFormatTag;
        
        // 处理WAVE_FORMAT_EXTENSIBLE格式
        if (formatTag == WAVE_FORMAT_EXTENSIBLE) {
            WAVEFORMATEXTENSIBLE* pExt = reinterpret_cast<WAVEFORMATEXTENSIBLE*>(pDeviceFormat);
            if (pExt->SubFormat == KSDATAFORMAT_SUBTYPE_IEEE_FLOAT) {
                formatTag = WAVE_FORMAT_IEEE_FLOAT;
            } else if (pExt->SubFormat == KSDATAFORMAT_SUBTYPE_PCM) {
                formatTag = WAVE_FORMAT_PCM;
            }
        }
        
        if (formatTag == WAVE_FORMAT_IEEE_FLOAT || 
            (pDeviceFormat->wBitsPerSample == 32 && formatTag != WAVE_FORMAT_PCM)) {
            // 处理32位浮点格式
            ProcessFloatAudio(input, inputBytes, output);
        } else if (pDeviceFormat->wBitsPerSample == 16) {
            // 处理16位整数格式
            ProcessInt16Audio(input, inputBytes, output);
        } else if (pDeviceFormat->wBitsPerSample == 32 || pDeviceFormat->wBitsPerSample == 24) {
            // 处理32位/24位整数格式
            ProcessInt32Audio(input, inputBytes, output);
        }
    }
    
    void ProcessInt16Audio(const BYTE* input, size_t inputBytes, std::vector<BYTE>& output) {
        const short* inputSamples = reinterpret_cast<const short*>(input);
        size_t numInputSamples = inputBytes / sizeof(short);
        size_t numInputFrames = numInputSamples / deviceChannels;
        
        // 如果采样率相同，直接复制数据
        if (deviceSampleRate == TARGET_SAMPLE_RATE && deviceChannels == TARGET_CHANNELS) {
            output.resize(inputBytes);
            memcpy(output.data(), input, inputBytes);
            return;
        }
        
        // 计算输出帧数
        size_t numOutputFrames = (numInputFrames * TARGET_SAMPLE_RATE) / deviceSampleRate;
        
        output.clear();
        output.reserve(numOutputFrames * sizeof(short));
        
        for (size_t i = 0; i < numOutputFrames; i++) {
            size_t inputFrame = (i * deviceSampleRate) / TARGET_SAMPLE_RATE;
            if (inputFrame >= numInputFrames) inputFrame = numInputFrames - 1;
            
            short sample = 0;
            if (deviceChannels == 2) {
                sample = (inputSamples[inputFrame * 2] + inputSamples[inputFrame * 2 + 1]) / 2;
            } else {
                sample = inputSamples[inputFrame];
            }
            
            output.push_back(sample & 0xFF);
            output.push_back((sample >> 8) & 0xFF);
        }
    }
    
    void ProcessFloatAudio(const BYTE* input, size_t inputBytes, std::vector<BYTE>& output) {
        const float* inputSamples = reinterpret_cast<const float*>(input);
        size_t numInputSamples = inputBytes / sizeof(float);
        size_t numInputFrames = numInputSamples / deviceChannels;
        
        size_t numOutputFrames = (numInputFrames * TARGET_SAMPLE_RATE) / deviceSampleRate;
        
        output.clear();
        output.reserve(numOutputFrames * sizeof(short));
        
        for (size_t i = 0; i < numOutputFrames; i++) {
            size_t inputFrame = (i * deviceSampleRate) / TARGET_SAMPLE_RATE;
            if (inputFrame >= numInputFrames) inputFrame = numInputFrames - 1;
            
            float floatSample = 0;
            if (deviceChannels == 2) {
                floatSample = (inputSamples[inputFrame * 2] + inputSamples[inputFrame * 2 + 1]) / 2.0f;
            } else {
                floatSample = inputSamples[inputFrame];
            }
            
            // 限制范围并转换为16位整数
            if (floatSample > 1.0f) floatSample = 1.0f;
            if (floatSample < -1.0f) floatSample = -1.0f;
            
            short sample = static_cast<short>(floatSample * 32767.0f);
            
            output.push_back(sample & 0xFF);
            output.push_back((sample >> 8) & 0xFF);
        }
    }
    
    void ProcessInt32Audio(const BYTE* input, size_t inputBytes, std::vector<BYTE>& output) {
        // 32位音频：通常是24位有效数据在32位容器中
        // 每样本4字节，按小端序解析
        size_t numInputFrames = inputBytes / (4 * deviceChannels);
        
        size_t numOutputFrames = (numInputFrames * TARGET_SAMPLE_RATE) / deviceSampleRate;
        
        output.clear();
        output.reserve(numOutputFrames * sizeof(short));
        
        for (size_t i = 0; i < numOutputFrames; i++) {
            size_t inputFrame = (i * deviceSampleRate) / TARGET_SAMPLE_RATE;
            if (inputFrame >= numInputFrames) inputFrame = numInputFrames - 1;
            
            // 解析32位样本（小端序）
            int intSample = 0;
            if (deviceChannels == 2) {
                const BYTE* left = input + (inputFrame * deviceChannels * 4);
                const BYTE* right = left + 4;
                
                int leftSample = left[0] | (left[1] << 8) | (left[2] << 16) | (left[3] << 24);
                int rightSample = right[0] | (right[1] << 8) | (right[2] << 16) | (right[3] << 24);
                
                // 转换为有符号32位
                if (leftSample & 0x80000000) leftSample |= ~0xFFFFFFFF;
                if (rightSample & 0x80000000) rightSample |= ~0xFFFFFFFF;
                
                intSample = (leftSample + rightSample) / 2;
            } else {
                const BYTE* samplePtr = input + (inputFrame * 4);
                intSample = samplePtr[0] | (samplePtr[1] << 8) | (samplePtr[2] << 16) | (samplePtr[3] << 24);
                if (intSample & 0x80000000) intSample |= ~0xFFFFFFFF;
            }
            
            // 从32位/24位转换为16位（右移16位或8位）
            // 先尝试右移16位（假设是32位有效数据）
            short sample = static_cast<short>(intSample >> 16);
            
            // 如果音量太小，尝试右移8位
            if (sample > -10 && sample < 10) {
                sample = static_cast<short>(intSample >> 8);
            }
            
            output.push_back(sample & 0xFF);
            output.push_back((sample >> 8) & 0xFF);
        }
    }

    void RecordLoop() {
        while (!shouldStop) {
            UINT32 packetLength = 0;
            HRESULT hr = pCaptureClient->GetNextPacketSize(&packetLength);
            if (FAILED(hr)) {
                continue;
            }

            while (packetLength != 0) {
                BYTE* pData = nullptr;
                UINT32 numFramesAvailable = 0;
                DWORD flags = 0;

                hr = pCaptureClient->GetBuffer(&pData, &numFramesAvailable, &flags, nullptr, nullptr);
                if (SUCCEEDED(hr)) {
                    if ((flags & AUDCLNT_BUFFERFLAGS_SILENT) == 0) {
                        size_t bytesToCopy = numFramesAvailable * pDeviceFormat->nBlockAlign;
                        
                        // 如果设备格式与目标格式不同，进行转换
                        if (deviceSampleRate != TARGET_SAMPLE_RATE || 
                            deviceChannels != TARGET_CHANNELS ||
                            pDeviceFormat->wBitsPerSample != BITS_PER_SAMPLE) {
                            ProcessAudio(pData, bytesToCopy, tempBuffer);
                            audioData.insert(audioData.end(), tempBuffer.begin(), tempBuffer.end());
                        } else {
                            audioData.insert(audioData.end(), pData, pData + bytesToCopy);
                        }
                    }
                    pCaptureClient->ReleaseBuffer(numFramesAvailable);
                }

                hr = pCaptureClient->GetNextPacketSize(&packetLength);
                if (FAILED(hr)) {
                    break;
                }
            }

            Sleep(10);
        }
    }
};

// 检查是否有按键输入，如果有则返回按键字符，否则返回 0
char checkForKeyPress() {
    if (_kbhit()) {
        int ch = _getch();
        // 忽略方向键等特殊键（它们会返回两个字节，第一个是 0 或 0xE0）
        if (ch == 0 || ch == 0xE0) {
            _getch(); // 消耗第二个字节
            return 0;
        }
        return (char)ch;
    }
    return 0;
}

int main() {
    SetConsoleOutputCP(CP_UTF8);
    
    printf("=== 音频录音程序 ===\n");
    printf("命令说明:\n");
    printf("  R - 开始录音\n");
    printf("  S - 停止录音并保存\n");
    printf("  Q - 退出程序\n");
    printf("====================\n\n");

    AudioRecorder recorder;
    if (!recorder.Initialize()) {
        printf("音频设备初始化失败!\n");
        printf("请按任意键退出...\n");
        _getch();
        return 1;
    }

    printf("音频设备初始化成功!\n\n");
    printf("提示：按 R 键开始录音，按 S 键停止录音并保存，然后自动退出\n\n");

    bool running = true;
    char cmd = 0;
    
    while (running) {
        // 检查是否有按键输入
        char key = checkForKeyPress();
        
        if (key != 0) {
            cmd = key;
            printf("%c\n", cmd);
            fflush(stdout);
        } else {
            // 没有按键时，短暂等待
            Sleep(50);
            continue;
        }

        switch (cmd) {
            case 'r':
            case 'R':
                if (!recorder.IsRecording()) {
                    recorder.StartRecording();
                    printf(">>> 正在录音中... (按 S 停止录音)\n");
                    fflush(stdout);
                } else {
                    printf("录音已经在进行中...\n");
                }
                break;

            case 's':
            case 'S':
                if (recorder.IsRecording()) {
                    recorder.StopRecording();
                    recorder.SaveToWAV("output.wav");
                    printf(">>> 录音已保存为 output.wav\n");
                    printf("程序即将退出...\n");
                    running = false;
                } else {
                    printf("当前没有在录音\n");
                }
                break;

            default:
                printf("无效命令，请输入 R 或 S\n");
                break;
        }
        
        cmd = 0; // 重置命令
    }

    return 0;
}
