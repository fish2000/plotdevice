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
    GPUImageHalftoneFilter *filter;
}

@property(nonatomic, retain) GPUImageHalftoneFilter *filter;

- (id)init;
- (NSImage *)process:(NSImage *)input;

@end