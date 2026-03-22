import Foundation
import Photos

enum ImportError: Error {
    case invalidArguments
    case authorizationDenied
    case importFailed(String)
}

func requestPermission() async throws {
    let status = await PHPhotoLibrary.requestAuthorization(for: .addOnly)
    switch status {
    case .authorized, .limited:
        return
    default:
        throw ImportError.authorizationDenied
    }
}

func importLivePhoto(photoURL: URL, videoURL: URL) async throws -> String {
    try await requestPermission()

    return try await withCheckedThrowingContinuation { continuation in
        var placeholderIdentifier: String?
        PHPhotoLibrary.shared().performChanges({
            let request = PHAssetCreationRequest.forAsset()
            let photoOptions = PHAssetResourceCreationOptions()
            photoOptions.shouldMoveFile = false
            request.addResource(with: .photo, fileURL: photoURL, options: photoOptions)

            let motionOptions = PHAssetResourceCreationOptions()
            motionOptions.shouldMoveFile = false
            request.addResource(with: .pairedVideo, fileURL: videoURL, options: motionOptions)
            placeholderIdentifier = request.placeholderForCreatedAsset?.localIdentifier
        }) { success, error in
            if success {
                continuation.resume(returning: placeholderIdentifier ?? "created")
                return
            }
            continuation.resume(
                throwing: ImportError.importFailed(error?.localizedDescription ?? "unknown error")
            )
        }
    }
}

@main
struct LivePhotoImporter {
    static func main() async {
        do {
            guard CommandLine.arguments.count == 3 else {
                throw ImportError.invalidArguments
            }
            let photoURL = URL(fileURLWithPath: CommandLine.arguments[1])
            let videoURL = URL(fileURLWithPath: CommandLine.arguments[2])
            let identifier = try await importLivePhoto(photoURL: photoURL, videoURL: videoURL)
            print(identifier)
            Foundation.exit(EXIT_SUCCESS)
        } catch ImportError.invalidArguments {
            fputs("usage: import_live_photo.swift <photo_path> <video_path>\n", stderr)
            Foundation.exit(EXIT_FAILURE)
        } catch ImportError.authorizationDenied {
            fputs("Photos access denied\n", stderr)
            Foundation.exit(EXIT_FAILURE)
        } catch ImportError.importFailed(let message) {
            fputs("Import failed: \(message)\n", stderr)
            Foundation.exit(EXIT_FAILURE)
        } catch {
            fputs("Unexpected error: \(error)\n", stderr)
            Foundation.exit(EXIT_FAILURE)
        }
    }
}
