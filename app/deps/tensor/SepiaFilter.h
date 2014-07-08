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

@interface SepiaFilter : NSObject {
    GPUImageSepiaFilter *filter;
}

@property(nonatomic, retain) GPUImageSepiaFilter *filter;

- (id)init;
- (NSImage *)process:(NSImage *)input;

@end