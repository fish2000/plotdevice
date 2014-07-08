//
//  filters.h
//  PlotDevice
//
//  Created by fish2k on 12/7/13.
//
//

#import <Foundation/Foundation.h>
#import <AppKit/AppKit.h>
#import <GPUImage/GPUImage.h>

@interface Filter : NSObject {
    NSImage *inputImage;
    NSImage *outputImage;
    GPUImageHalftoneFilter *filter;
}

@property(nonatomic, copy) NSImage *inputImage;
@property(nonatomic, copy) NSImage *outputImage;
@property(nonatomic, retain) GPUImageHalftoneFilter *filter;


- (id)init;
- (NSImage *)process:(NSImage *)input;

@end